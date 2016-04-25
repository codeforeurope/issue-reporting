import operator

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from issues import analysis
from issues.models import Issue, MediaFile, Service
from issues.services import attach_files_to_issue, get_issues, save_file_to_db

from .serializers import IssueDetailSerializer, IssueSerializer, ServiceSerializer


class RequestBaseAPIView(APIView):
    item_tag_name = 'request'
    root_tag_name = 'requests'


class IssueList(RequestBaseAPIView):

    def get(self, request, format=None):
        service_object_id = request.query_params.get('service_object_id', None)
        service_object_type = request.query_params.get('service_object_type', None)

        if service_object_id is not None and service_object_type is None:
            raise ValidationError(
                "If service_object_id is included in the request, then service_object_type must be included.")

        queryset = get_issues(
            service_request_ids=request.query_params.get('service_request_id', None),
            service_codes=request.query_params.get('service_code', None),
            start_date=request.query_params.get('start_date', None),
            end_date=request.query_params.get('end_date', None),
            statuses=request.query_params.get('status', None),
            service_object_type=service_object_type,
            service_object_id=service_object_id,
            lat=request.query_params.get('lat', None),
            lon=request.query_params.get('long', None),
            radius=request.query_params.get('radius', None),
            updated_after=request.query_params.get('updated_after', None),
            updated_before=request.query_params.get('updated_before', None),
            search=request.query_params.get('search', None),
            agency_responsible=request.query_params.get('agency_responsible', None),
            order_by=request.query_params.get('order_by', None),
            use_limit=True
        )

        serializer = IssueSerializer(queryset, many=True,
                                        context={'extensions': request.query_params.get('extensions', 'false')})
        return Response(serializer.data)

    def post(self, request, format=None):
        # TODO: (for future releases) add API key rules
        serializer = IssueDetailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            new_issue = serializer.save()

            # save files in the same manner as it's done in issue form
            if request.FILES:
                for filename, file in request.FILES.items():
                    save_file_to_db(file, new_issue.service_request_id)
                files = MediaFile.objects.filter(form_id=new_issue.service_request_id)
                if files:
                    attach_files_to_issue(request, new_issue, files)

            response_data = {
                'service_request_id': new_issue.service_request_id,
                'service_notice': ''
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IssueDetail(RequestBaseAPIView):

    def get(self, request, service_request_id, format=None):
        queryset = get_issues(
            service_request_ids=service_request_id,
            service_codes=request.query_params.get('service_code', None),
            start_date=request.query_params.get('start_date', None),
            end_date=request.query_params.get('end_date', None),
            statuses=request.query_params.get('status', None),
            lat=request.query_params.get('lat', None),
            lon=request.query_params.get('long', None),
            radius=request.query_params.get('radius', None),
            updated_after=request.query_params.get('updated_after', None),
            updated_before=request.query_params.get('updated_before', None),
            search=request.query_params.get('search', None),
            order_by=request.query_params.get('order_by', None)
        )

        serializer = IssueSerializer(queryset, many=True,
                                        context={'extensions': request.query_params.get('extensions', 'false')})
        return Response(serializer.data)


class ServiceList(APIView):
    item_tag_name = 'service'
    root_tag_name = 'services'

    def get(self, request, format=None):
        queryset = Service.objects.all()
        serializer = ServiceSerializer(queryset, many=True)

        return Response(serializer.data)


def get_service_statistics(request, service_code):
    try:
        service = Service.objects.get(service_code=service_code)
    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'unknown service code'},
                            status=status.HTTP_404_NOT_FOUND)

    statistics = get_service_item_statistics(service)
    return JsonResponse(statistics)


def get_services_statistics(request):
    service_statistics = []
    for service in Service.objects.all():
        item = get_service_item_statistics(service)
        service_statistics.append(item)

    # Sort the rows by "total" column
    service_statistics.sort(key=operator.itemgetter('total'), reverse=True)

    return JsonResponse(service_statistics, safe=False)


def get_service_item_statistics(service):
    item = {}
    service_code = service.service_code

    avg = analysis.get_avg_duration(analysis.get_closed_by_service_code(service_code))
    median = analysis.get_median_duration(analysis.get_closed_by_service_code(service_code))

    item["service_code"] = service.service_code
    item["service_name"] = service.service_name
    item["total"] = analysis.get_total_by_service(service_code)
    item["closed"] = analysis.get_closed_by_service(service_code)
    item["avg_sec"] = int(avg.total_seconds())
    item["median_sec"] = int(median.total_seconds())

    return item


def get_agency_item_statistics(agency_responsible):
    item = {}

    avg = analysis.get_avg_duration(analysis.get_closed_by_agency_responsible(agency_responsible))
    median = analysis.get_median_duration(analysis.get_closed_by_agency_responsible(agency_responsible))

    item["agency_responsible"] = agency_responsible
    item["total"] = analysis.get_total_by_agency(agency_responsible)
    item["closed"] = analysis.get_closed_by_agency(agency_responsible)
    item["avg_sec"] = int(avg.total_seconds())
    item["median_sec"] = int(median.total_seconds())

    return item


def get_agency_statistics(request, agency):
    issues_with_agency = Issue.objects.filter(agency_responsible__iexact=agency).count()

    if issues_with_agency == 0:
        return JsonResponse({'status': 'error', 'message': 'unknown agency name'},
                            status=status.HTTP_404_NOT_FOUND)

    statistics = get_agency_item_statistics(agency)
    return JsonResponse(statistics)


def get_agencies_statistics(request):
    agency_statistics = []
    agencies = Issue.objects.all().distinct("agency_responsible")
    for agency in agencies:
        item = get_agency_item_statistics(agency.agency_responsible)
        agency_statistics.append(item)

    # Sort the rows by "total" column
    agency_statistics.sort(key=operator.itemgetter('total'), reverse=True)

    return JsonResponse(agency_statistics, safe=False)


def get_agency_responsible_list(request):
    issues = Issue.objects.all().distinct("agency_responsible").order_by('agency_responsible')
    agencies = [f.agency_responsible for f in issues]
    return JsonResponse(agencies, safe=False)
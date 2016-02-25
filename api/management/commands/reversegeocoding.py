from django.core.management import BaseCommand
from django.db.models import Q

from api.geocoding.geocoding import reverse_geocode
from api.models import Feedback


class Command(BaseCommand):
    help = 'Fill addresses for the feedbacks with empty address_string field.'

    def handle(self, *args, **options):
        feedbacks = Feedback.objects.filter(Q(address_string__isnull=True) | Q(address_string__exact=''))
        for f in feedbacks:
            address = reverse_geocode(f.lat, f.lon)
            if f.lat == 0 or f.lon == 0:
                continue
            f.address_string = address
            f.save()
        print('reverse geocoding complete')

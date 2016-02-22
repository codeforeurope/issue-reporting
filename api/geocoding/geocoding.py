import json
import urllib
from urllib.error import URLError

from django.conf import settings


def reverse_geocode(lat, lon):
    reverse_geocoding_url = settings.REVERSE_GEO_URL.format(lat, lon)
    print('url to send: {}'.format(reverse_geocoding_url))

    try:
        response = urllib.request.urlopen(reverse_geocoding_url)
        content = response.read()
        json_data = json.loads(content.decode("utf8"))
    except ValueError:
        print('Decoding JSON has failed')
        return
    except URLError:
        print('Invalid URL: {}'.format(reverse_geocoding_url))
        return
    pass

    results_json = json_data.get('results', None)
    if results_json:
        res = results_json[0]
        street = res['street']['name']['fi'] + ' ' + res['number']
        municipality = res['street']['municipality'].capitalize()
        address_string = street + ', ' + municipality
        print(address_string)
        return address_string

    print('address not found')
    return ''

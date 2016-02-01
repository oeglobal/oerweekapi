from pprint import pprint
import requests
from requests.auth import HTTPBasicAuth
import json

from django.core.management.base import BaseCommand
from django.conf import settings

from web.importer import import_project

class Command(BaseCommand):
    help = "Sync data from WP"

    def add_arguments(self, parser):
        parser.add_argument('--id', type=int)
        parser.add_argument('--type', type=str)
        parser.add_argument('--maxto', type=int)

    def handle(self, *args, **options):
        auth = HTTPBasicAuth(settings.WP_USER, settings.WP_PASS)

        url = "{}/wp/v2/users/me".format(settings.WP_API)
        print(url)
        pprint(json.loads(requests.get(url, auth=auth).content.decode()))


        if options.get('id'):
            import_project(options.get('id'))

        if options.get('maxto'):
            for i in range(200, options.get('maxto') + 1):
                import_project(i)

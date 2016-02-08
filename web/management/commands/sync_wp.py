from pprint import pprint
import requests
from requests.auth import HTTPBasicAuth
import json

from django.core.management.base import BaseCommand
from django.conf import settings

from web.importer import import_resource, import_openphoto
from web.models import Resource, OpenPhoto

class Command(BaseCommand):
    help = "Sync data from WP"

    def add_arguments(self, parser):
        parser.add_argument('--id', type=int)
        parser.add_argument('--type', type=str)
        parser.add_argument('--maxto', type=int)
        parser.add_argument('--refresh', type=bool)

    def handle(self, *args, **options):
        auth = HTTPBasicAuth(settings.WP_USER, settings.WP_PASS)

        url = "{}/wp/v2/users/me".format(settings.WP_API)
        print(url)
        pprint(json.loads(requests.get(url, auth=auth).content.decode()))

        post_type = options.get('type')

        if options.get('id'):
            if post_type == 'openphoto':
                import_openphoto(post_id=options.get('id'))
            else:
                import_resource(post_type=options.get('type'), post_id=options.get('id'))


        if options.get('maxto'):
            for i in range(1, options.get('maxto') + 1):
                if post_type == 'openphoto':
                    import_openphoto(post_id=i)
                else:
                    import_resource(post_type=post_type, post_id=i)

        if options.get('refresh'):
            if ( options.get('type') == 'resource' or not options.get('type') ):
                for resource in Resource.objects.all().order_by('-id'):
                    resource.refresh()

            if ( options.get('type') == 'openphoto' or not options.get('type') ):
                for photo in OpenPhoto.objects.all().order_by('-id'):
                    photo.refresh()

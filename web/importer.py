import json
import requests
from pprint import pprint
from requests.auth import HTTPBasicAuth

from django.conf import settings

from .models import Resource

def import_project(project_id):
    auth = HTTPBasicAuth(settings.WP_USER, settings.WP_PASS)

    url = "{}/wp/v2/project/{}".format(settings.WP_API, project_id)

    data = json.loads(requests.get(url, auth=auth).content.decode())
    pprint(data)
    if data.get('code') in ['rest_post_invalid_id', 'rest_forbidden']:
        return

    try:
        resource = Resource.objects.get(post_id=project_id)
    except Resource.DoesNotExist:
        resource = Resource(post_id=project_id, post_type='project')

    resource.title = data.get('title').get('rendered')
    resource.slug = data.get('slug')
    resource.post_status = data.get('post_status')
    resource.content = data.get('content').get('rendered')

    acf = data.get('acf', {})

    if acf:
        resource.form_id = acf.get('form_id')
        resource.contact = acf.get('extra_contact', '')
        resource.institution = acf.get('extra_institution', '')
        resource.form_language = acf.get('extra_language', '')
        resource.license = acf.get('extra_license', '')
        resource.link = acf.get('extra_link', '')

    resource.save()

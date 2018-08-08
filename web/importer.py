import json
import requests
import arrow
from requests.auth import HTTPBasicAuth

from django.conf import settings

from .models import Resource, Category


def import_submission(data):
    # data = data.get('data', {}).get('attributes', {})
    from pprint import pprint
    pprint(data)

    resource = Resource(post_id=0)
    resource.raw_post = json.dumps(data)

    resource.post_status = 'draft'

    resource.firstname = data.get('firstname')
    resource.lastname = data.get('lastname')

    resource.email = data.get('email')
    resource.institution = data.get('institution') or ''
    resource.institution_url = data.get('institutionurl') or ''
    if resource.institution_url and not resource.institution_url.startswith('http'):
        resource.institution_url = 'http://' + resource.institution_url

    resource.country = data.get('country')
    resource.city = data.get('city')

    resource.title = data.get('title')
    resource.content = data.get('description')
    resource.form_language = data.get('language')
    resource.link = data.get('link') or ''
    if resource.link and not resource.link.startswith('http'):
        resource.link = 'http://' + resource.link
    resource.linkwebroom = data.get('linkwebroom') or ''
    if resource.linkwebroom and not resource.linkwebroom.startswith('http'):
        resource.linkwebroom = 'http://' + resource.linkwebroom
    resource.opentags = data.get('opentags') or []

    if data.get('license'):
        resource.license = data.get('license', '')

    if data.get('contributiontype') in ['event']:
        if data.get('eventtype') == 'local':
            resource.post_type = 'event'
            resource.event_online = False
            resource.event_directions = data.get('directions', '')
            resource.event_type = 'local'

        elif data.get('eventtype') == 'online':
            resource.post_type = 'event'
            resource.event_online = True
            resource.event_type = 'online'

        if data.get('localeventtype') in ['other_local', 'other_online']:
            resource.event_other_text = 'online'

        if data.get('facilitator'):
            resource.event_facilitator = data.get('facilitator')

        resource.event_time = arrow.get(data.get('datetime')).datetime

        resource.save()
    else:
        resource.post_type = data.get('contributiontype')
        resource.save()

    # Categories
    if data.get('is-primary'):
        cat, is_created = Category.objects.get_or_create(
            wp_id=0,
            name='Primary or Secondary Education',
            slug='primary-or-secondary-education')
        resource.categories.add(cat)

    if data.get('is-higher'):
        cat, is_created = Category.objects.get_or_create(
            wp_id=0,
            name='Higher Education',
            slug='higher-education')
        resource.categories.add(cat)

    if data.get('is-community'):
        cat, is_created = Category.objects.get_or_create(
            wp_id=0,
            name='Community and Technical Colleges',
            slug='community-and-technical-colleges')
        resource.categories.add(cat)

    return resource

import json
import requests
import arrow

from requests.auth import HTTPBasicAuth

from django.conf import settings

from .models import Resource, OpenPhoto, Category


def import_resource(post_type, post_id):
    if post_type not in ['project', 'resource', 'event']:
        return

    auth = HTTPBasicAuth(settings.WP_USER, settings.WP_PASS)

    url = "{}/wp/v2/{}/{}".format(settings.WP_API, post_type, post_id)

    data = json.loads(requests.get(url, auth=auth).content.decode())
    print(url)
    # pprint(data)
    if data.get('code') in ['rest_post_invalid_id', 'rest_forbidden', 'rest_no_route']:
        print(data.get('code'))
        return

    try:
        resource = Resource.objects.get(post_id=post_id)
    except Resource.DoesNotExist:
        resource = Resource(post_id=post_id, post_type=post_type)

    resource.title = data.get('title').get('rendered')
    resource.slug = data.get('slug')
    resource.post_status = data.get('post_status')
    resource.content = data.get('content').get('rendered')
    resource.created = arrow.get(data.get('date')).datetime

    acf = data.get('acf', {})

    if acf:
        resource.form_id = acf.get('form_id') or None
        resource.contact = acf.get('extra_contact', '')
        resource.email = acf.get('contact_email', '')
        resource.institution = acf.get('extra_institution', '')
        resource.form_language = acf.get('extra_language', '')
        resource.license = acf.get('extra_license', '')
        resource.link = acf.get('extra_link', '')
        resource.city = acf.get('extra_location_city', '')
        resource.country = acf.get('extra_location_country', '')

        resource.event_type = acf.get('event_type', '')
        resource.event_source_datetime = acf.get('extra_source_datetime', '')
        resource.event_source_timezone = acf.get('extra_source_timezone', '')

        if resource.event_type and not resource.event_source_timezone:
            resource.event_source_timezone = '(GMT -0:00) London, Western Europe, Lisbon, Casablanca'

        if acf.get('event_time'):
            resource.event_time = arrow.get(acf.get('event_time')).datetime
        else:
            if (acf.get('extra_source_datetime')):
                if resource.event_type in ['webinar', 'online']:
                    timezone = resource.event_source_timezone.split(')')[0].split(' ')[1]
                    if len(timezone) == 5:
                        timezone = "{}0{}".format(timezone[0], timezone[1:])
                    try:
                        event_time = "{} {}".format(acf.get('extra_source_datetime'), timezone)
                        event_time_utc = arrow.get(event_time, 'YYYY-MM-DD HH:mm a ZZ').datetime
                        resource.event_time = event_time_utc
                    except arrow.parser.ParserError:
                        pass
                else:
                    try:
                        resource.event_time = arrow.get(acf.get('extra_source_datetime')).datetime
                    except arrow.parser.ParserError:
                        resource.event_time = arrow.get(acf.get('extra_source_datetime'),
                                                        ['MM/DD/YYYY HH:mm p']).datetime

    if data.get('_links', {}).get('https://api.w.org/featuredmedia'):
        media_url = data.get('_links', {}).get('https://api.w.org/featuredmedia')[0].get('href')
        media_data = json.loads(requests.get(media_url, auth=auth).content.decode())

        image_url = media_data.get('media_details', {}).get('sizes', {}).get('large', {}).get('source_url')
        if image_url:
            resource.image_url = image_url
        else:
            image_url = media_data.get('media_details', {}).get('sizes', {}).get('full', {}).get('source_url')
            resource.image_url = image_url

    resource.save()


def import_openphoto(post_id):
    auth = HTTPBasicAuth(settings.WP_USER, settings.WP_PASS)

    url = "{}/wp/v2/{}/{}".format(settings.WP_API, 'openphoto', post_id)

    data = json.loads(requests.get(url, auth=auth).content.decode())
    print(url)
    # pprint(data)
    if data.get('code') in ['rest_post_invalid_id', 'rest_forbidden', 'rest_no_route']:
        return

    try:
        photo = OpenPhoto.objects.get(post_id=post_id)
    except OpenPhoto.DoesNotExist:
        photo = OpenPhoto(post_id=post_id)

    photo.title = data.get('title').get('rendered')
    photo.slug = data.get('slug')
    photo.post_status = data.get('post_status')
    photo.created = arrow.get(data.get('date')).datetime
    photo.content = data.get('content')

    acf = data.get('acf', {})
    if acf:
        photo.city = acf.get('openphoto_city', '')
        photo.country = acf.get('openphoto_country', '')
        photo.url = acf.get('openphoto_url', '')

        photomap = acf.get('openphoto_map')
        if photomap:
            photo.lat = photomap.get('lat')
            photo.lng = photomap.get('lng')
            photo.address = photomap.get('address', '')

    photo.save()


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

    resource.country = data.get('country')
    resource.city = data.get('city')

    resource.title = data.get('title')
    resource.content = data.get('description')
    resource.form_language = data.get('language')
    resource.link = data.get('link') or ''
    resource.linkwebroom = data.get('linkwebroom') or ''
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

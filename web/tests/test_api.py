# -*- coding: utf-8 -*-
import pytest
import json
import arrow
from pprint import pprint

from django.core import mail

from web.models import Resource


@pytest.mark.client
@pytest.mark.django_db
def test_submission_event_online(rf, client, db, normal_user):
    data = {
        'data': {
            'attributes': {'email': 'mike.jones@example.com',
                           'language': 'German',
                           'post_type': 'event',
                           'eventtype': 'online',
                           'is_community': True,
                           'institution': 'OEC',
                           'institutionurl': 'http://www.oeconsortium.org',
                           'directions': None,
                           'archive': True,
                           'link': 'www.oeconsortium.org/events/online/20',
                           'description': 'Description of Webinar about OER',
                           'country': 'United States',
                           'lastname': 'Jones',
                           'is_primary': False,
                           'firstname': 'Mike',
                           'license': 'CC-BY',
                           'datetime': '2018-03-27T19:00:00+02:00',
                           'is_higher': True,
                           'title': 'Webinar about OER',
                           'city': 'New York',
                           'image_url': '',
                           'opentags': ['Open Research', 'Open Policy']
                           },
            'type': 'submission'
        }
    }

    # client.login(username='user', password='password')
    response = client.post('/api/submission', content_type='application/vnd.api+json', data=json.dumps(data))
    pprint(response.json())
    assert data.get('data').get('attributes').get('title') in str(response.content), 'Submission failed'

    resource = Resource.objects.latest('id')
    assert resource.title == data.get('data').get('attributes').get('title')
    assert resource.content == data.get('data').get('attributes').get('description')
    assert resource.event_type == 'online'
    assert resource.event_online is True
    assert resource.post_status == 'draft'

    # check that validator adds http:// on www only submissions
    assert resource.link == 'http://www.oeconsortium.org/events/online/20'


@pytest.mark.client
@pytest.mark.django_db
def test_submission_event_local(rf, client, db, normal_user):
    data = {
        'post_type': 'event',
        'eventtype': 'local',

        'firstname': 'Mike',
        'lastname': 'Jones',
        'email': 'mike@example.com',

        'institution': 'OEC',
        'institutionurl': 'http://www.oeconsortium.org',
        'country': 'United States',
        'city': 'Baltimore',

        'link': 'http://www.oeconsoritum.org/event/14',

        'event_time': '2018-04-12T15:30:00+02:00',
        'directions': 'Main Street 5, Baltimore',

        'title': 'Creative Destruction:  An ‘Open Textbook’ disrupting personal and institutional praxis',
        'archive': True,

        'description': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit,'
                       'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim'
                       'veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo '
                       'consequat.Duis aute irure dolor in reprehenderit in voluptate velit esse cillum'
                       'dolore eu fugiat nulla pariatur.Excepteur sint occaecat cupidatat non proident',
        'language': 'English',
        'is_primary': False,
        'is_higher': True,
        'is_community': True,
        'opentags': ['Open Research', 'Open Policy']
    }

    client.login(username='user', password='password')
    response = client.post('/api/submission', content_type='application/json', data=json.dumps(data))

    resource = Resource.objects.latest('id')
    assert resource.title == data.get('title')
    assert resource.event_type == 'local'
    assert resource.event_time == arrow.get(data.get('event_time')).datetime


@pytest.mark.client
@pytest.mark.django_db
def test_submission_oer_resource(rf, client, db, normal_user):
    data = {
        'post_type': 'resource',
        'city': 'Washington, DC',
        'is_primary': False,
        'firstname': 'Mike',
        'lastname': 'Smith',
        'title': 'Building for Scale: Updates to Google Maps APIs Standard Plan',
        'description': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit',
        'is_community': True,
        'country': 'United States',
        'archive': False,
        'institution': 'OEC',
        'link': 'http://www.oeconsortium.org/web/resource/',
        'email': 'mike2@example.com',
        'is_higher': True,
        'institutionurl': 'http://www.oeconsortium.org',
        'language': 'English',
        'datetime': '2018-03-27T00:00:00+02:00',
        'license': 'CC-BY-SA',
        'directions': None,
        'linkwebroom': None,
        'opentags': ['Open Research', 'Open Policy']
    }

    client.login(username='user', password='password')
    response = client.post('/api/submission', content_type='application/json', data=json.dumps(data))
    print(response.content)
    assert data.get('title') in str(response.content), 'OER Resource Submission failed'

    resource = Resource.objects.latest('id')
    assert resource.title == data.get('title')
    assert resource.slug == 'building-for-scale-updates-to-google-maps-apis-standard-plan'


@pytest.mark.client
@pytest.mark.django_db
def test_submission_project(rf, client, db, normal_user):
    data = {
        'archive': False,
        'description': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod'
                       '\ntempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim '
                       'veniam,\nquis nostrud exercitation ullamco laboris nisi ut aliquip ex ea'
                       'commodo\nconsequat. Duis aute irure dolor in reprehenderit in voluptate '
                       'velit esse\ncillum dolore eu fugiat nulla pariatur. Excepteur sint '
                       'occaecat cupidatat non\nproident, sunt in culpa qui officia deserunt mollit'
                       'anim id est laborum.',
        'city': 'San Francisco, CA',
        'lastname': 'Smith',
        'link': 'http://www.oeconsortium.org/project/showcase/',
        'country': 'United States',
        'institutionurl': 'http://www.oeconsortium.org/',
        'language': 'English',
        'is_higher': False,
        'datetime': '2018-03-27T00:00:00+02:00',
        'license': 'Freely accessible',
        'institution': 'OEC',
        'directions': None,
        'title': 'Engineers Create The First Dust-Sized Wireless Sensors That Can Be Implanted Into The Human Body',
        'firstname': 'Mike',
        'is_community': True,
        'is_primary': True,
        'email': 'mike3@example.com',
        'contributiontype': 'project',
        'opentags': ['Open Research', 'Open Policy'],
        'post_type': 'resource'
    }

    client.login(username='user', password='password')
    response = client.post('/api/submission', content_type='application/json', data=json.dumps(data))
    assert data.get('title') in str(response.content), 'OER Resource Submission failed'

    resource = Resource.objects.latest('id')
    assert resource.title == data.get('title')


@pytest.mark.client
@pytest.mark.django_db
def test_submission_online_event_other(rf, client, db, normal_user):
    data = {
        'license': None,
        'institution': '',
        'archive': True,
        'post_type': 'event',
        'eventtype': 'online',
        'city': 'London',
        'directions': None,
        'is_primary': False,
        'is_higher': True,
        'language': 'English',
        'lastname': 'Jones',
        'country': 'United Kingdom',
        'email': 'mike2@example.com',
        'firstname': 'Mike',
        'title': 'Twitter Chat',
        'datetime': '2018-03-27T00:00:00+02:00',
        'link': '',
        'description': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod'
                       '\ntempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam',
        'is_community': False,
        'institutionurl': '',
        'opentags': ['Open Research', 'Open Policy']
    }

    client.login(username='user', password='password')
    response = client.post('/api/submission', content_type='application/json', data=json.dumps(data))
    assert data.get('title') in str(response.content), 'OER Resource Submission failed'

    resource = Resource.objects.latest('id')
    assert resource.title == data.get('title')


@pytest.mark.client
@pytest.mark.django_db
def test_submission_email(rf, client, db, normal_user):
    data = {
        'license': 'other',
        'institution': '',
        'archive': True,
        'post_type': 'event',
        'eventtype': 'local',
        'city': 'London',
        'directions': None,
        'is_primary': False,
        'is_higher': True,
        'language': 'English',
        'lastname': 'Jones',
        'country': 'United Kingdom',
        'email': 'mike2@example.com',
        'firstname': 'Mike',
        'title': 'Building for Scale: Updates to Google Maps APIs Standard Plan',
        'datetime': '2018-03-27T00:00:00+02:00',
        'link': '',
        'description': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod',
        'is_community': False,
        'institutionurl': '',
        'opentags': ['Open Research', 'Open Policy']
    }

    client.login(username='user', password='password')
    response = client.post('/api/submission', content_type='application/json', data=json.dumps(data))
    assert data.get('title') in str(response.content), 'OER Resource Submission failed'

    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == 'OEW: We have received your submission'

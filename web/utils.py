from rest_framework_jwt.utils import jwt_payload_handler
from rest_framework_json_api.exceptions import exception_handler
from raven.contrib.django.raven_compat.models import client

from web.serializers import SubmissionResourceSerializer


def custom_jwt_payload_handler(user):
    payload = jwt_payload_handler(user)

    payload['staff'] = user.is_staff
    return payload


def custom_drf_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(context.get('view').get_serializer_class(), SubmissionResourceSerializer):
        client.captureMessage('Form Submission Validation Error', level='debug', extra=exc.get_full_details())
    else:
        try:
            if exc.status_code != 404:
                client.captureMessage('General DRF error', level='debug', extra=exc.get_full_details())
        except:
            client.captureMessage('General DRF error', level='debug', extra=exc.get_full_details())
            
    return response

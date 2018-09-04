from rest_framework_jwt.utils import jwt_payload_handler
from rest_framework_json_api.exceptions import exception_handler
from raven.contrib.django.raven_compat.models import client


def custom_jwt_payload_handler(user):
    payload = jwt_payload_handler(user)

    payload['staff'] = user.is_staff
    return payload


def custom_drf_exception_handler(exc, context):
    response = exception_handler(exc, context)
    client.captureMessage('Form Submission Validation Error', level='debug', extra=exc.get_full_details())

    return response

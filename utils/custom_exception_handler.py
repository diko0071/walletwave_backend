from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    exception_class = exc.__class__.__name__

    if exception_class == 'AuthenticationFailed':
        response.data['error'] = 'Invalid username or password.'
        response.data['status_code'] = response.status_code

    if exception_class == 'NotAuthenticated':
        response.data['error'] = 'Authentication credentials were not provided.'
        response.data['status_code'] = response.status_code

    if exception_class == 'InvalidToken':
        response.data['error'] = 'Token is expired.'
        response.data['status_code'] = response.status_code

    return response


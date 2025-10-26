from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    """
    Custom exception handler for consistent error responses
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            'error': 'Validation failed',
            'details': response.data
        }
        
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            return Response(custom_response_data, status=status.HTTP_400_BAD_REQUEST)
    
    return response

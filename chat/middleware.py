from django.http import JsonResponse
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import BlacklistedAccessToken

class BlacklistTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = self._get_token_from_request(request)
        if token and self._is_token_blacklisted(token):
            return JsonResponse({'detail': 'Token has been invalidated. Please login again.'}, status=status.HTTP_401_UNAUTHORIZED)
        return self.get_response(request)

    def _get_token_from_request(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]
        return None

    def _is_token_blacklisted(self, token):
        return BlacklistedAccessToken.objects.filter(token=token).exists()
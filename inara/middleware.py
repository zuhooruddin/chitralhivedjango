from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import UntypedToken
from inara.models import TokenBlacklist
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer

class TokenBlacklistMiddleware(MiddlewareMixin):

    def process_request(self, request):
        try:
            token = request.headers['Authorization'].split()[1]
            UntypedToken(token)
        except KeyError:
            return None
        except Exception:
            return None

        if TokenBlacklist.objects.filter(token=token).exists():
            response = Response({'error': 'Invalid token. Please log in again.'}, status=status.HTTP_401_UNAUTHORIZED)
            response.accepted_renderer = JSONRenderer()
            response.accepted_media_type = "application/json"
            response.renderer_context = {}
            response.render()
            return response
        

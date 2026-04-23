from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import UntypedToken
from inara.models import TokenBlacklist
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from django.conf import settings
from django.utils.cache import patch_cache_control

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
        

class StaticMediaCacheHeadersMiddleware(MiddlewareMixin):
    """
    Add long-lived cache headers for static/media files.
    Keeps UI identical; improves Lighthouse "cache lifetimes" for assets served by Django.
    """

    def process_response(self, request, response):
        path = request.path or ""

        static_prefix = getattr(settings, "STATIC_URL", "") or ""
        media_prefix = getattr(settings, "MEDIA_URL", "") or ""

        is_static = static_prefix and path.startswith(static_prefix)
        is_media = media_prefix and path.startswith(media_prefix)

        if is_static or is_media:
            # If upstream already set caching, keep it.
            if not response.headers.get("Cache-Control"):
                patch_cache_control(
                    response,
                    public=True,
                    max_age=31536000,
                    immutable=True,
                )
        return response

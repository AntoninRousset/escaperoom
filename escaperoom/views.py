from django.conf import settings
from django.http import HttpResponse
from django.views import static
from drf_spectacular.views import (
    SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
)

schema = SpectacularAPIView.as_view()
swagger = SpectacularSwaggerView.as_view(url_name='schema')
redoc = SpectacularRedocView.as_view(url_name='schema')


class XAccelRedirectResponse(HttpResponse):
    def __init__(self, path, *args, protected=True, **kwargs):
        super().__init__(*args, **kwargs)
        if protected:
            path = settings.X_ACCEL_REDIRECT_PREFIX + path
        self['X-Accel-Redirect'] = path
        del self['Content-Type']


def serve_media(request, path):
    path = str(path)
    if settings.X_ACCEL_REDIRECT:
        return XAccelRedirectResponse(settings.MEDIA_URL + path)
    else:
        return static.serve(request, path, settings.MEDIA_ROOT)


def serve_static(request, path):
    path = str(path)
    if settings.X_ACCEL_REDIRECT:
        return XAccelRedirectResponse(settings.STATIC_URL + path)
    else:
        return static.serve(request, path, settings.STATIC_ROOT)


def app(request, path):
    return serve_static(request, 'dist/index.html')

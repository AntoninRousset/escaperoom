from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.defaults import page_not_found
from escaperoom import views


api_urlpatterns = [
    path('engine/', include('engine.urls'), name='engine'),
    path('network', include('network.urls'), name='network'),
    path('schema/', views.schema, name='schema'),
    path('schema/swagger-ui/', views.swagger, name='swagger-ui'),
    path('schema/redoc/', views.redoc, name='redoc'),
    re_path('(.*)', page_not_found),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_urlpatterns), name='api'),
    path(settings.STATIC_URL[1:] + '<path:path>', views.serve_static),
    path(settings.MEDIA_URL[1:] + 'media/<path:path>', views.serve_media),
    re_path('(?P<path>.*)', views.app, name='app'),
]

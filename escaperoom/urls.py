from django.contrib import admin
from django.contrib.staticfiles.views import serve
from django.urls import include, path, re_path
from django.views.defaults import page_not_found
from escaperoom import views
from rest_framework.routers import SimpleRouter


router = SimpleRouter()
router.register(r'states', views.StateViewSet, basename='state')
router.register(r'statetransitions', views.StateTransitionViewSet,
                basename='statetransition')

api_urlpatterns = [
    # path('schema/', views.schema, name='schema'),  # breaks OAG
    path('schema/swagger-ui/', views.swagger, name='swagger-ui'),
    path('schema/redoc/', views.redoc, name='redoc'),
] + router.urls

urlpatterns = [
    path('api/', include(api_urlpatterns), name='api'),
    re_path('api/(.*)', page_not_found),
    path('admin/', admin.site.urls),
    re_path('admin/(.*)', page_not_found),
    re_path('.*', serve, {'path': 'dist/index.html'}, name='app'),
]

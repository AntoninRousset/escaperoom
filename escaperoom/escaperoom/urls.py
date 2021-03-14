from django.contrib import admin
from django.urls import include, path, re_path
from django.views.defaults import page_not_found
from escaperoom import views
from rest_framework.routers import SimpleRouter


router = SimpleRouter()
router.register(r'states', views.StateViewSet, basename='state')
router.register(r'statetransitions', views.StateTransitionViewSet,
                basename='statetransition')

urlpatterns = [
    path('api/schema', views.schema, name='schema'),
    path('api/schema/redoc', views.redoc, name='redoc'),
    path('api/', include(router.urls), name='api'),
    re_path('api/(.*)', page_not_found),
    path('admin/', admin.site.urls),
    re_path('admin/(.*)', page_not_found),
    re_path('(?P<path>.*)', views.AppView.as_view(), name='app'),
]

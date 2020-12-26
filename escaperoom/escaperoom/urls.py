from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('fsm', views.fsm, name='fsm'),
    path('measurement', views.measurement, name='measurement'),
    path('admin/', admin.site.urls),
]

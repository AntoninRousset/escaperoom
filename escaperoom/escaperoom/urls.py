from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('states', views.states, name='states'),
    path('admin/', admin.site.urls),
]

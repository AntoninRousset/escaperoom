from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import redirect, reverse
from django.template import loader

from . import models


def index(request):
    return redirect(reverse('dashboard'))


def dashboard(request):
    template = loader.get_template('dashboard.html')
    return HttpResponse(template.render({}, request))


def states(request):
    states = serializers.serialize('json', models.State.objects.all())
    return HttpResponse(states, content_type='application/json')

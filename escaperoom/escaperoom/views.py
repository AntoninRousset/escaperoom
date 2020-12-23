from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, reverse
from django.template import loader

from . import models, serializers


def index(request):
    return redirect(reverse('dashboard'))


def dashboard(request):
    template = loader.get_template('dashboard.html')
    return HttpResponse(template.render({}, request))


def states(request):
    objects = models.State.objects.all()
    serializer = serializers.StateSerializer(objects, many=True)
    return JsonResponse(serializer.data)

from django.http import HttpResponse, JsonResponse
from django.template import loader

from . import models, serializers


def index(request):
    template = loader.get_template('app.html')
    return HttpResponse(template.render({}, request))


def states(request):
    objects = models.State.objects.filter(parent=None).all()
    serializer = serializers.StateSerializer(objects, many=True)
    return JsonResponse(serializer.data)

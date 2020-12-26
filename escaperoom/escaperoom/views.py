from django.http import HttpResponse, JsonResponse
from django.template import loader

from . import models
from .serializers import StateSerializer, StateTransitionSerializer


def index(request):
    template = loader.get_template('app.html')
    return HttpResponse(template.render({}, request))


def fsm(request):
    states = models.State.objects.filter(parent=None).all()
    transitions = models.StateTransition.objects.all()

    return JsonResponse({
        'states': StateSerializer(states, many=True).data,
        'transitions': StateTransitionSerializer(transitions, many=True).data,
    })


def measurement(request):
    return HttpResponse('')

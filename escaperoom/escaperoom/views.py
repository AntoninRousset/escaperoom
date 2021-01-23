from asgiref.sync import sync_to_async
from django.http import HttpResponse, JsonResponse
from django.template import loader

from . import models
from .serializers import StateSerializer, StateTransitionSerializer


def index(request):
    template = loader.get_template('app.html')
    return HttpResponse(template.render({}, request))


async def fsm(request):
    states = await sync_to_async(models.State.objects.all)()
    transitions = await sync_to_async(models.StateTransition.objects.all)()
    return JsonResponse({
        'states': StateSerializer(states, many=True).data,
        'transitions': StateTransitionSerializer(transitions, many=True).data
    })

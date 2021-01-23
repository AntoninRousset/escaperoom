import json
from django.http import HttpResponse, JsonResponse
from django.template import loader

from . import models
from .serializers import StateSerializer, StateTransitionSerializer


def index(request):
    template = loader.get_template('app.html')
    return HttpResponse(template.render({}, request))


def fsm(request):
    if request.method == 'GET':
        states = models.State.objects.all()
        transitions = models.StateTransition.objects.all()
        return JsonResponse({
            'states': StateSerializer(states, many=True).data,
            'transitions': StateTransitionSerializer(
                transitions, many=True
            ).data
        })
    elif request.method == 'POST':
        data = json.loads(request.data)
        states = StateSerializer(data['states'])
        print(states)

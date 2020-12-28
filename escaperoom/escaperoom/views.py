from django.http import HttpResponse, JsonResponse
from django.template import loader

from . import brain, models
from .serializers import MachineSerializer


def index(request):
    template = loader.get_template('app.html')
    return HttpResponse(template.render({}, request))


def fsm(request):
    root_machines = models.Machine.objects.filter(parent_state=None).all()
    return JsonResponse(
        MachineSerializer(root_machines, many=True).data, safe=False
    )


def measurement(request):
    brain.request_states_check()
    return HttpResponse('')

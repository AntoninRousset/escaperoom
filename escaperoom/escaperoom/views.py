from django.http import HttpResponse
from django.shortcuts import redirect, reverse
from django.template import loader


def index(request):
    return redirect(reverse('dashboard'))


def dashboard(request):
    template = loader.get_template('dashboard.html')
    return HttpResponse(template.render({}, request))

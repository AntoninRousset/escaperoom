import django_filters
from django.db.models import Q
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView
from escaperoom import models, serializers
from rest_framework.viewsets import ModelViewSet


schema = SpectacularAPIView.as_view()
redoc = SpectacularRedocView.as_view(url_name='schema')


class AppView(TemplateView):
    template_name = 'app.html'


class StateViewSet(ModelViewSet):
    queryset = models.State.objects.all()
    serializer_class = serializers.StateSerializer
    filterset_fields = ('room',)


class StateTransitionFilter(django_filters.FilterSet):
    room = django_filters.ModelChoiceFilter(
        queryset=models.Room.objects.all(), method='filter_by_room'
    )

    class Meta:
        model = models.StateTransition
        fields = tuple()

    def filter_by_room(self, queryset, name, value):
        return queryset.filter(
            Q(from_state__room=value) | Q(to_state__room=value)
        )


class StateTransitionViewSet(ModelViewSet):
    queryset = models.StateTransition.objects.all()
    serializer_class = serializers.StateTransitionSerializer
    filter_class = StateTransitionFilter

import django_filters
from django.db.models import Q
from drf_spectacular.utils import extend_schema
from drf_spectacular.views import (
    SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
)
from escaperoom import models, serializers
from rest_framework.viewsets import ModelViewSet


schema = SpectacularAPIView.as_view()
swagger = SpectacularSwaggerView.as_view(url_name='schema')
redoc = SpectacularRedocView.as_view(url_name='schema')


@extend_schema(tags=['engine'])
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


@extend_schema(tags=['engine'])
class StateTransitionViewSet(ModelViewSet):
    queryset = models.StateTransition.objects.all()
    serializer_class = serializers.StateTransitionSerializer
    filter_class = StateTransitionFilter

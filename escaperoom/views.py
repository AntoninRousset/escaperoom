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
    filterset_fields = ['room']


@extend_schema(tags=['engine'])
class StateTransitionViewSet(ModelViewSet):
    queryset = models.StateTransition.objects.all()
    serializer_class = serializers.StateTransitionSerializer
    filterset_fields = ['from_state__room', 'to_state__room']  # TODO room

from drf_spectacular.utils import extend_schema
from engine import models, serializers
from rest_framework.viewsets import ModelViewSet


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

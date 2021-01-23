from rest_framework.serializers import (
    ModelSerializer, PrimaryKeyRelatedField
)
from rest_framework_bulk import BulkListSerializer, BulkSerializerMixin

from . import models


class FsmSerializer(ModelSerializer):
    class Meta:
        model = models.Fsm
        fields = ('states', 'transitions')


class StateSerializer(BulkSerializerMixin, ModelSerializer):
    class Meta:
        model = models.State
        list_serializer_class = BulkListSerializer
        fields = ('id', 'name', 'parent', 'children', 'is_entrypoint',
                  'is_active', 'x', 'y')


class StateTransitionSerializer(BulkSerializerMixin, ModelSerializer):
    src = PrimaryKeyRelatedField(
        source='from_state', queryset=models.State.objects.all()
    )
    dest = PrimaryKeyRelatedField(
        source='to_state', queryset=models.State.objects.all()
    )

    class Meta:
        model = models.StateTransition
        list_serializer_class = BulkListSerializer
        fields = ('id', 'src', 'dest')

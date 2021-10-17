from engine import models
from rest_framework import serializers


class StateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = models.State
        fields = (
            'id', 'room', 'name', 'parent', 'is_entrypoint', 'is_active', 'x',
            'y'
        )


class StateTransitionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    src = serializers.PrimaryKeyRelatedField(
        source='from_state', queryset=models.State.objects.all()
    )
    dest = serializers.PrimaryKeyRelatedField(
        source='to_state', queryset=models.State.objects.all()
    )

    class Meta:
        model = models.StateTransition
        fields = ('id', 'src', 'dest')

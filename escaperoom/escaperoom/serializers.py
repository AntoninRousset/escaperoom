from escaperoom import models
from rest_framework import serializers


class StateListSerializer(serializers.ListSerializer):
    pass


class StateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = models.State
        list_serializer_class = StateListSerializer
        fields = ('id', 'room', 'name', 'parent', 'is_entrypoint', 'is_active',
                  'x', 'y')


class StateTransitionListSerializer(serializers.ListSerializer):
    pass


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
        list_serializer_class = StateTransitionListSerializer
        fields = ('id', 'src', 'dest')

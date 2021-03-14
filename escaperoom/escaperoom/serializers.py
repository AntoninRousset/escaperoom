from escaperoom import models
from rest_framework import serializers


class StateListSerializer(serializers.ListSerializer):
    pass


class StateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    local_id = serializers.IntegerField(required=False)

    class Meta:
        model = models.State
        list_serializer_class = StateListSerializer
        fields = ('id', 'local_id', 'room', 'name', 'parent', 'is_entrypoint',
                  'is_active', 'x', 'y')


class StateTransitionListSerializer(serializers.ListSerializer):
    pass


class StateTransitionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    local_id = serializers.IntegerField(required=False)
    src = serializers.PrimaryKeyRelatedField(
        source='from_state', queryset=models.State.objects.all()
    )
    dest = serializers.PrimaryKeyRelatedField(
        source='to_state', queryset=models.State.objects.all()
    )

    class Meta:
        model = models.StateTransition
        list_serializer_class = StateTransitionListSerializer
        fields = ('id', 'local_id', 'src', 'dest')


'''
class FsmSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)
    states = StateSerializer(many=True)
    transitions = StateTransitionSerializer(many=True)

    class Meta:
        model = models.Fsm
        fields = ('id', 'states', 'transitions')

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Deleting objects before editing others that relates on them causes
        "FOREIGN KEY constraint failed"
        Maybe deletions should not be done in update...
        """

        states_to_delete = set()
        for validated_state_data in validated_data.pop('states', []):
            state_id = validated_state_data.pop('id', None)
            deleted = validated_state_data.pop('deleted', False)

            validated_state_data['machine'] = validated_state_data.get(
                'machine', instance
            )

            try:
                state = models.State.objects.get(id=state_id)
                if deleted:
                    states_to_delete.add(state)
                else:
                    for attr, value in validated_state_data.items():
                        setattr(state, attr, value)
                    state.save()
            except models.fsm.State.DoesNotExist:
                if not deleted:
                    models.State.objects.create(**validated_state_data)

        for state in states_to_delete:
            state.delete()

        transitions = validated_data.pop('transitions', [])

        return instance
'''

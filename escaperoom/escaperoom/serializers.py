from rest_framework import serializers

from . import models


class DictSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        result = list()
        for item in data:
            representation = self.child.to_representation(item)
            result.append((item.id, representation))
        return result

    @property
    def data(self):
        ret = super(DictSerializer, self).data
        return serializers.ReturnDict(ret, serializer=self)


class MachineSerializer(serializers.ModelSerializer):
    states = serializers.SerializerMethodField()
    transitions = serializers.SerializerMethodField()

    class Meta:
        model = models.Machine
        fields = ('id', 'parent_state', 'states', 'transitions')

    def get_states(self, machine):
        return StateSerializer(machine.states.all(), many=True).data

    def get_transitions(self, machine):
        return StateTransitionSerializer(
            machine.transitions.all(), many=True
        ).data


class StateSerializer(serializers.ModelSerializer):
    submachine = serializers.SerializerMethodField()

    class Meta:
        model = models.State
        fields = ('id', 'name', 'machine', 'submachine', 'is_entrypoint',
                  'is_active', 'x', 'y')

    def get_submachine(self, state):
        try:
            return MachineSerializer(state.submachine).data
        except models.Machine.DoesNotExist:
            return None


class StateTransitionSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.StateTransition
        fields = ('id', 'from_state', 'to_state')

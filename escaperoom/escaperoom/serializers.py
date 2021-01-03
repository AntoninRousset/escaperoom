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


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.State
        fields = ('id', 'name', 'parent', 'children', 'is_entrypoint',
                  'is_active', 'x', 'y')


class StateTransitionSerializer(serializers.ModelSerializer):
    src = serializers.SerializerMethodField()
    dest = serializers.SerializerMethodField()

    class Meta:
        model = models.StateTransition
        fields = ('id', 'src', 'dest')

    def get_src(self, state):
        return state.from_state.id

    def get_dest(self, state):
        return state.to_state.id

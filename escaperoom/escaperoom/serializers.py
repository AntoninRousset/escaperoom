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
        list_serializer_class = DictSerializer
        fields = ('id', 'name', 'is_active', 'is_entrypoint', 'x', 'y',
                  'parent', 'children')

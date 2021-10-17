from network import models
from rest_framework import serializers


class AttributeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Attribute
        fields = ('name', 'variable',)


class ModuleSerializer(serializers.ModelSerializer):
    attributes = AttributeSerializer(many=True)

    class Meta:
        model = models.Module
        fields = ('id', 'node', 'attributes',)


class NodeSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True)

    class Meta:
        model = models.Node
        fields = ('id', 'name', 'modules')

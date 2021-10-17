from drf_spectacular.utils import extend_schema
from network import models, serializers
from rest_framework.viewsets import ModelViewSet


@extend_schema(tags=['network'])
class AttributeViewSet(ModelViewSet):
    queryset = models.Attribute.objects.all()
    serializer_class = serializers.AttributeSerializer


@extend_schema(tags=['network'])
class ModuleViewSet(ModelViewSet):
    queryset = models.Module.objects.all()
    serializer_class = serializers.ModuleSerializer


@extend_schema(tags=['network'])
class NodeViewSet(ModelViewSet):
    queryset = models.Node.objects.all()
    serializer_class = serializers.NodeSerializer

import uuid
from django.db import models


class Attribute(models.Model):

    class AttributeType(models.TextChoices):
        STR = 'STR', 'string'
        INT = 'INT', 'int'
        FLOAT = 'FLO', 'float'
        BOOL = 'BOO', 'boolean'

    module = models.ForeignKey('Module', related_name='attributes',
                               on_delete=models.CASCADE)
    name = models.TextField(blank=True)
    type = models.CharField(max_length=3, choices=AttributeType.choices)
    variable = models.ForeignKey('engine.Variable', related_name='attribute',
                                 on_delete=models.SET_NULL, blank=True,
                                 null=True)

    def __str__(self):
        return self.name


class Module(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    node = models.ForeignKey('Node', related_name='modules',
                             on_delete=models.CASCADE)
    name = models.TextField(blank=True)

    def __str__(self):
        return self.name if self.name else 'no name'


class Node(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.TextField(blank=True)

    def __str__(self):
        return self.name if self.name else 'no name'

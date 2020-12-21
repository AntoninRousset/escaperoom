from django.db import models


class Condition(models.Model):
    type = models.ForeignKey('ConditionType', on_delete=models.CASCADE)
    variable1 = models.ForeignKey('Variable', related_name='+',
                                  on_delete=models.RESTRICT)  # TODO PROTECT?
    variable2 = models.ForeignKey('Variable', related_name='+',
                                  on_delete=models.RESTRICT)  # TODO PROTECT?


class ConditionType(models.Model):
    name = models.CharField(max_length=64, unique=True)


class Measurement(models.Model):
    timestamp = models.DateTimeField()
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE)
    value = models.TextField()

    class Meta:
        unique_together = ('timestamp', 'variable')

    def __str__(self):
        return f'{self.timestamp.isoformat()}: {self.variable} = {self.value}'


class Machine(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE)


class State(models.Model):
    name = models.CharField(max_length=128)
    conditions = models.ManyToManyField('Condition', related_name='+')
    machine = models.ForeignKey('Machine', on_delete=models.CASCADE)
    initial = models.BooleanField()

    class Meta:
        unique_together = ('machine', 'initial')


class Variable(models.Model):
    name = models.CharField(max_length=128, unique=True)
    type = models.ForeignKey('VariableType', related_name='+',
                             on_delete=models.RESTRICT)
    default_value = models.TextField(null=True)
    locked_at = models.DateTimeField(null=True)

    def __str__(self):
        return f'"{self.name}" ({self.type})'

    def _convert_value(self, value):
        if value is None:
            return value
        if self.type.name == 'str':
            return str(value)
        elif self.type.name == 'int':
            return int(value)
        elif self.type.name == 'float':
            return float(value)
        elif self.type.name == 'bool':
            return bool(value)
        elif self.type.name == 'toggle':
            return bool(float(value) % 2)
        raise RuntimeError('Unknown variable type')

    def value(self, at=None):
        try:
            measurements = Measurement.objects.filter(variable=self.id)
            if at is not None:
                measurements = measurements.filter(timestamp__lte=at)
            value = measurements.latest('timestamp').value
        except Measurement.DoesNotExist:
            value = self.default_value
        return self._convert_value(value)


class VariableType(models.Model):
    name = models.CharField(max_length=16, unique=True)

    def __str__(self):
        return str(self.name)

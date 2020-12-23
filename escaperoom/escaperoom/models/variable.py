from django.db import models


class Operator(models.Model):
    type = models.ForeignKey('OperatorType', on_delete=models.CASCADE)
    variable_a = models.ForeignKey('Variable', related_name='+',
                                   on_delete=models.RESTRICT)  # TODO PROTECT?
    variable_b = models.ForeignKey('Variable', related_name='+',
                                   on_delete=models.RESTRICT)  # TODO PROTECT?

    def result(self, at=None):
        return self.type.convert(
            a=self.variable_a.value(at=at),
            b=self.variable_b.value(at=at)
        )


class OperatorType(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def convert(self, a, b):
        if a is None or b is None:
            return None
        if self.name == 'equal':
            return a == b
        if self.name == 'not equal':
            return a != b
        if self.name == 'greater or equal':
            return a >= b
        if self.name == 'lower or equal':
            return a <= b
        if self.name == 'greater':
            return a > b
        if self.name == 'lower':
            return a < b
        if self.name == 'add':
            return a + b
        if self.name == 'substract':
            return a - b
        if self.name == 'multiply':
            return a * b
        if self.name == 'divide':
            return a / b


class Measurement(models.Model):
    timestamp = models.DateTimeField()
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE)
    value = models.TextField()

    class Meta:
        unique_together = ('timestamp', 'variable')

    def __str__(self):
        return f'{self.timestamp.isoformat()}: {self.variable} = {self.value}'


class Variable(models.Model):
    name = models.CharField(max_length=128, unique=True)
    type = models.ForeignKey('VariableType', related_name='+',
                             on_delete=models.RESTRICT)
    default_value = models.TextField(null=True)
    locked_at = models.DateTimeField(null=True)
    operator = models.ForeignKey('Operator', null=True,
                                 on_delete=models.CASCADE)

    def __str__(self):
        return f'"{self.name}" ({self.type})'

    def value(self, at=None):
        if self.operator is not None:
            value = self.operator.result(at=at)
        else:
            try:
                measurements = Measurement.objects.filter(variable=self.id)
                if at is not None:
                    measurements = measurements.filter(timestamp__lte=at)
                value = measurements.latest('timestamp').value
            except Measurement.DoesNotExist:
                value = self.default_value
        return self.type.convert(value)


class VariableType(models.Model):
    name = models.CharField(max_length=16, unique=True)

    def __str__(self):
        return str(self.name)

    def convert(self, value):
        if value is None:
            return value
        if self.name == 'str':
            return str(value)
        if self.name == 'int':
            return int(value)
        if self.name == 'float':
            return float(value)
        if self.name == 'bool':
            return bool(value)
        if self.name == 'toggle':
            return bool(float(value) % 2)
        raise RuntimeError('Unknown variable type')

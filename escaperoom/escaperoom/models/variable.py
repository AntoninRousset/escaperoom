from django.db import models


class Operator(models.Model):

    class OperatorType(models.TextChoices):
        EQUAL = 'EQU', 'equal'
        NOT_EQUAL = 'NEQ', 'not equal'
        GREATER_OR_EQUAL = 'GTE', 'greater or equal'
        LOVER_OR_EQUAL = 'LTE', 'lower or equal'
        GREATER = 'GT', 'greater'
        LOWER = 'LT', 'lower'
        ADD = 'ADD', 'add'
        SUBSTRACT = 'SUB', 'substract'
        MULTIPLY = 'MUL', 'multiply'
        DIVIDE = 'DIV', 'divide'

    type = models.CharField(max_length=3, choices=OperatorType.choices)
    variable_a = models.ForeignKey('Variable', related_name='+',
                                   on_delete=models.RESTRICT)  # TODO PROTECT?
    variable_b = models.ForeignKey('Variable', related_name='+',
                                   on_delete=models.RESTRICT)  # TODO PROTECT?

    def convert(self, a, b):
        if a is None or b is None:
            return None
        if self.type == 'EQU':
            return a == b
        if self.type == 'NEQ':
            return a != b
        if self.type == 'GTE':
            return a >= b
        if self.type == 'LTE':
            return a <= b
        if self.type == 'GT':
            return a > b
        if self.type == 'LT':
            return a < b
        if self.type == 'ADD':
            return a + b
        if self.type == 'SUB':
            return a - b
        if self.type == 'MUL':
            return a * b
        if self.type == 'DIV':
            return a / b

    def result(self, at=None):
        return self.convert(
            a=self.variable_a.value(at=at),
            b=self.variable_b.value(at=at)
        )


class Measurement(models.Model):
    timestamp = models.DateTimeField()
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE)
    value = models.TextField()

    class Meta:
        unique_together = ('timestamp', 'variable')

    def __str__(self):
        return f'{self.timestamp.isoformat()}: {self.variable} = {self.value}'


class Variable(models.Model):

    class VariableType(models.TextChoices):
        STR = 'STR', 'string'
        INT = 'INT', 'int'
        FLOAT = 'FLO', 'float'
        BOOL = 'BOO', 'boolean'
        TOGGLE = 'TOG', 'toggle'

    name = models.CharField(max_length=128, unique=True)
    type = models.CharField(max_length=3, choices=VariableType.choices)

    default_value = models.TextField(null=True)
    locked_at = models.DateTimeField(null=True)
    operator = models.ForeignKey('Operator', null=True,
                                 on_delete=models.CASCADE)

    def __str__(self):
        return f'"{self.name}" ({self.type})'

    def convert(self, value):
        if value is None:
            return value
        if self.type == 'STR':
            return str(value)
        if self.type == 'INT':
            return int(value)
        if self.type == 'FLO':
            return float(value)
        if self.type == 'BOO':
            return bool(value)
        if self.type == 'TOG':
            return bool(float(value) % 2)
        raise RuntimeError(f'Unknown variable type "{self.type}"')

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
        return self.convert(value)

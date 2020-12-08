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

    @property
    def converted_value(self):
        return self.variable.convert_value(self.value)

    def __str__(self):
        return f'{self.timestamp.isoformat()}: {self.variable} = {self.value}'


class State(models.Model):
    name = models.CharField(max_length=128)
    conditions = models.ManyToManyField('Condition', related_name='+')


class Variable(models.Model):
    name = models.CharField(max_length=128)
    type = models.ForeignKey('VariableType', related_name='+',
                             on_delete=models.RESTRICT)

    def convert_value(self, value):
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
        raise RuntimeError('Unknown variable value')

    def __str__(self):
        return f'"{self.name}" ({self.type})'


class VariableType(models.Model):

    name = models.CharField(max_length=16, unique=True)

    def __str__(self):
        return str(self.name)

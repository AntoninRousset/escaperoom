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

    def __str__(self):
        return f'{self.type}({self.variable_a},{self.variable_b})'

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


class State(models.Model):
    name = models.CharField(max_length=64, blank=True)
    parent = models.ForeignKey(
        'self', related_name='children', on_delete=models.CASCADE, blank=True,
        null=True
    )
    room = models.ForeignKey(
        'escaperoom.Room', related_name='states', on_delete=models.CASCADE
    )
    is_entrypoint = models.BooleanField(default=False)
    x = models.IntegerField()
    y = models.IntegerField()

    def __str__(self):
        return self.name if self.name else 'no name'

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(parent=models.F('id')),
                name='%(app_label)s_%(class)s_not_own_parent',
            ),
        ]

    @classmethod
    def active_states(self, at=None):
        return {state for state in State.objects.all() if state.is_active(at)}

    def is_active(self, at=None) -> bool:
        try:
            changes = StateChange.objects.filter(state=self.id)
            if at is not None:
                changes = changes.filter(timestamp__lte=at)
            return changes.latest('timestamp').value
        except StateChange.DoesNotExist:
            return False


class StateChange(models.Model):
    timestamp = models.DateTimeField()
    state = models.ForeignKey('State', on_delete=models.CASCADE)
    value = models.BooleanField()

    def __str__(self):
        return f'{self.state} [{self.timestamp.isoformat()}]'


class StateTransition(models.Model):
    conditions = models.ManyToManyField('engine.Variable', related_name='+')
    from_state = models.ForeignKey('State',
                                   related_name='transitions_from',
                                   on_delete=models.CASCADE)
    to_state = models.ForeignKey('State', related_name='transitions_to',
                                 on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(to_state=models.F('from_state')),
                name='%(app_label)s_%(class)s_different_states',
            )
        ]

    def __str__(self):
        return f'{self.from_state} -> {self.to_state}'


class Variable(models.Model):

    class VariableType(models.TextChoices):
        STRING = 'STR', 'string'
        INTEGER = 'INT', 'int'
        FLOATING = 'FLO', 'float'
        BOOLEAN = 'BOO', 'boolean'
        TOGGLE = 'TOG', 'toggle'

    name = models.CharField(max_length=128, unique=True, blank=True)
    type = models.CharField(max_length=3, choices=VariableType.choices)

    default_value = models.TextField(blank=True)
    locked_at = models.DateTimeField(blank=True, null=True)
    operator = models.ForeignKey('Operator', blank=True, null=True,
                                 on_delete=models.CASCADE)

    def __str__(self):
        return self.name if self.name else 'no name'

    def convert(self, value):
        if value is None or value == '':
            return None
        if self.type == self.VariableType.STRING:
            return str(value)
        if self.type == self.VariableType.INTEGER:
            return int(value)
        if self.type == self.VariableType.FLOATING:
            return float(value)
        if self.type == self.VariableType.BOOLEAN:
            return bool(float(value))
        if self.type == self.VariableType.TOGGLE:
            return bool(float(value) % 2)
        raise RuntimeError(f'Unknown variable type "{self.type}"')

    def value(self, at=None):
        if self.operator is not None:
            value = self.operator.result(at=at)
        else:
            try:
                changes = VariableChange.objects.filter(variable=self.id)
                if at is not None:
                    changes = changes.filter(timestamp__lte=at)
                value = changes.latest('timestamp').value
            except VariableChange.DoesNotExist:
                value = self.default_value
        return self.convert(value)

    def save(self, *args, **kwargs):
        if self.value is not None and self.value != '':
            if self.type == self.VariableType.BOOLEAN:
                self.value = int(bool(self.value))
            elif self.type == self.VariableType.TOGGLE:
                self.value = int(bool(self.value))
            self.value = str(self.value)
        super().save(*args, **kwargs)


class VariableChange(models.Model):
    timestamp = models.DateTimeField()
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE)
    value = models.TextField()

    class Meta:
        unique_together = ('timestamp', 'variable')

    def __str__(self):
        return f'{self.variable} [{self.timestamp.isoformat()}]'

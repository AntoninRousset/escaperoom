from django.db import models


class Room(models.Model):
    pass


class State(models.Model):
    name = models.CharField(max_length=64)
    parent = models.ForeignKey('self', related_name='children', null=True,
                               on_delete=models.CASCADE)
    room = models.ForeignKey('Room', related_name='states',
                             on_delete=models.CASCADE)
    is_entrypoint = models.BooleanField(default=False)
    x = models.IntegerField()
    y = models.IntegerField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(parent=models.F('id')),
                name='%(app_label)s_%(class)s_not_own_parent',
            ),
        ]

    def __init__(self, *args, local_id=None, **kwargs):
        super().__init__(*args, **kwargs)

        if local_id is not None:
            self.local_id = local_id

    @classmethod
    def active_states(self, at=None):
        return {state for state in State.objects.all() if state.is_active(at)}

    def is_active(self, at=None):
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


class StateTransition(models.Model):
    '''
    Nothing prevents a transition between states in different rooms. Is this a
    bug or feature?
    '''
    from_state = models.ForeignKey('State', related_name='transitions_from',
                                   on_delete=models.CASCADE)
    to_state = models.ForeignKey('State', related_name='transitions_to',
                                 on_delete=models.CASCADE)

    def __init__(self, *args, local_id=None, **kwargs):
        super().__init__(*args, **kwargs)

        if local_id is not None:
            self.local_id = local_id

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(to_state=models.F('from_state')),
                name='%(app_label)s_%(class)s_different_states',
            )
        ]

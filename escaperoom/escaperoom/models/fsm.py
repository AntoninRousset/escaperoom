from django.db import models


class Fsm(models.Model):
    pass


class State(models.Model):
    name = models.CharField(max_length=64)
    parent = models.ForeignKey('State', related_name='children', null=True,
                               on_delete=models.CASCADE)
    machine = models.ForeignKey('Fsm', related_name='states',
                                on_delete=models.CASCADE)
    is_entrypoint = models.BooleanField(default=False)
    x = models.IntegerField()
    y = models.IntegerField()

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
    machine = models.ForeignKey('Fsm', related_name='transitions',
                                on_delete=models.CASCADE)
    from_state = models.ForeignKey('State', related_name='transitions_from',
                                   on_delete=models.CASCADE)
    to_state = models.ForeignKey('State', related_name='transitions_to',
                                 on_delete=models.CASCADE)
    #condition = models.ForeignKey('Variable', related_name='+',
    #                              on_delete=models.RESTRICT)

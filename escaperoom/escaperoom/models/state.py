from django.db import models


class Machine(models.Model):
    parent_state = models.OneToOneField('State', related_name='submachine',
                                        null=True, on_delete=models.CASCADE)

    @property
    def transitions(self):
        return StateTransition.objects.filter(
            from_state__in=self.states.all()
        )


class State(models.Model):
    name = models.CharField(max_length=64, null=True)
    machine = models.ForeignKey('Machine', related_name='states',
                                on_delete=models.CASCADE)
    is_entrypoint = models.BooleanField(default=False)
    x = models.IntegerField()
    y = models.IntegerField()

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
    from_state = models.ForeignKey('State', related_name='transitions_from',
                                   on_delete=models.CASCADE)
    to_state = models.ForeignKey('State', related_name='transitions_to',
                                 on_delete=models.CASCADE)
    #condition = models.ForeignKey('Variable', related_name='+',
    #                              on_delete=models.RESTRICT)

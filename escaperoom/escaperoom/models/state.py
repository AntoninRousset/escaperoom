from django.db import models


class State(models.Model):
    name = models.CharField(max_length=64, null=True)
    parent = models.ForeignKey('State', null=True, related_name='children',
                               on_delete=models.CASCADE)
    is_entrypoint = models.BooleanField(default=False)

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
    from_state = models.ForeignKey('State', related_name='+',
                                   on_delete=models.CASCADE)
    to_state = models.ForeignKey('State', related_name='+',
                                 on_delete=models.CASCADE)

from django.db import models


class Variable(models.Model):
    name = models.TextField()


class Measurement(models.Model):
    timestamp = models.DateTimeField()
    variable = models.ForeignKey(Variable, on_delete=models.CASCADE)
    value = models.FloatField()

    class Meta:
        db_table = 'measurement'
        unique_together = (('timestamp', 'variable'),)

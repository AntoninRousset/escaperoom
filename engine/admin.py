from django.contrib import admin
from engine import models


@admin.register(models.Operator)
class OperatorAdmin(admin.ModelAdmin):
    pass


@admin.register(models.State)
class StateAdmin(admin.ModelAdmin):
    pass


@admin.register(models.StateTransition)
class StateTransitionAdmin(admin.ModelAdmin):
    pass


@admin.register(models.StateChange)
class StateChangeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Variable)
class VariableAdmin(admin.ModelAdmin):
    pass


@admin.register(models.VariableChange)
class VariableChangeAdmin(admin.ModelAdmin):
    pass

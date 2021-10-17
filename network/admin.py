from django.contrib import admin
from network import models


@admin.register(models.Attribute)
class AttributeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Module)
class ModuleAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Node)
class NodeAdmin(admin.ModelAdmin):
    pass

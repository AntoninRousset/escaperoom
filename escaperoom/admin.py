from django.contrib import admin
from escaperoom import models


@admin.register(models.Room)
class RoomAdmin(admin.ModelAdmin):
    pass

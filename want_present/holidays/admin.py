from django.contrib import admin
from .models import Holiday


@admin.register(Holiday)
class HolidaysAdmin(admin.ModelAdmin):
    pass

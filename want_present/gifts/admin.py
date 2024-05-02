from django.contrib import admin
from .models import Gift


@admin.register(Gift)
class GiftsAdmin(admin.ModelAdmin):
    pass

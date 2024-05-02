from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Subscribe
from django.contrib.auth.models import Group


User = get_user_model()


@admin.register(User)
class UsersAdmin(admin.ModelAdmin):
    pass


@admin.register(Subscribe)
class SubscribesAdmin(admin.ModelAdmin):
    pass


admin.site.unregister(Group)

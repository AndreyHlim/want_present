from gifts.models import Gift
from holidays.models import Holiday
from rest_framework.permissions import BasePermission


class OnlyAuthorOrAdmin(BasePermission):
    """
    Разрешение на изменение/удаление пользователя только для автора
    или администратора. Остальным только чтение объекта.
    """
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Gift) or isinstance(obj, Holiday):
            obj = obj.user
        return request.user.is_superuser or request.user == obj

from rest_framework.permissions import SAFE_METHODS, BasePermission


class AuthorStaffOrReadOnly(BasePermission):
    """
    Разрешение на изменение только для служебного персонала и автора.
    Остальным только чтение объекта.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user.id_telegram is not None
            and request.user.is_authenticated
            and request.user.is_active
            and (
                request.user.id_telegram == obj.user.id_telegram
                or request.user.is_staff
            )
        )


class OnlyAuthor(BaseException):
    """
    Разрешение на изменение/удаление праздника только для автора.
    Остальным только чтение объекта.
    """

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user


class OnlyAuthorOrAdmin(OnlyAuthor):
    """
    Разрешение на изменение/удаление пользователя только для автора.
    или администратора. Остальным только чтение объекта.
    """

    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or request.user == obj

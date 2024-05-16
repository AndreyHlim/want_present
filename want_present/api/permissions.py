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

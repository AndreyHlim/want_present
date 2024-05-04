from rest_framework import serializers
from holidays.models import Holiday, User
from users.models import Subscribe


class HolidaySerializer(serializers.ModelSerializer):
    """
    Сериализатор модели 'Праздники'.
    Используется для отображения списка праздников.
    """

    class Meta:
        model = Holiday
        fields = ('id', 'name', 'date', 'user')


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели 'Пользователи'.
    Используется для отображения списка пользователей.
    """

    class Meta:
        model = User
        fields = ('id_telegram', 'address', 'is_open', 'username')


class SubscribeSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели 'Подписки'.
    Используется для отображения перечня подписок.
    """

    class Meta:
        model = Subscribe
        fields = ('user', 'subscribe', 'is_congratulate', 'name')

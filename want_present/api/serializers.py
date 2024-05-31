from datetime import datetime

from constants import CONSTANTS
from gifts.models import Gift
from holidays.models import Holiday, User
from rest_framework import serializers
from users.models import Subscribe


class HolidaySerializer(serializers.ModelSerializer):
    """
    Сериализатор модели 'Праздники'.
    Используется для отображения списка праздников.
    """

    class Meta:
        model = Holiday
        fields = ('id', 'name', 'date', 'user')

    def validate_date(self, value):
        if value < datetime.now().date():
            raise serializers.ValidationError(
                'Нельзя создавать ближайшую дату празднования в прошлом.'
            )
        elif value >= datetime.now().date().replace(
            year=datetime.now().date().year+CONSTANTS['LIFE_SPAN']
        ):
            raise serializers.ValidationError(
                'Нельзя создавать дату празднования в будущем '
                'более чем на {0} лет.'.format(CONSTANTS['LIFE_SPAN'])
            )
        return value


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


class GiftSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели 'Подарки'.
    Используется для отображения желаемых подарков пользователей.
    """
    user = UserSerializer()
    event = HolidaySerializer()

    class Meta:
        model = Gift
        fields = (
            'id', 'short_name', 'user', 'hyperlink', 'is_donated',
            'is_booked', 'is_want', 'event', 'comment',
        )

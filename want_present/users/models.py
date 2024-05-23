from constants import CONSTANTS

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models


class Profile(AbstractUser):
    """Кастомная модель пользователя."""

    USERNAME_FIELD = 'id_telegram'
    REQUIRED_FIELDS = ['username',]

    username = models.CharField(
        'Имя пользователя',
        max_length=50,
        unique=False,
    )
    id_telegram = models.IntegerField(
        'ID пользователя в Telegram',
        primary_key=True,
    )
    address = models.CharField(
        'Адрес для почтовых отправлений пользователю',
        max_length=CONSTANTS['MAX_ADDRESS'],
        null=True,
        blank=True,
        default='',
    )
    is_open = models.BooleanField(
        'Желание получать анонимный подарок',
        default=False,
        blank=False,
        null=False,
    )

    def __str__(self) -> str:
        return f'{self.id_telegram} ({self.username})'


User = get_user_model()


class Subscribe(models.Model):
    """Модель подписок пользователей."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='subscriptions',
    )
    subscribe = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Кого поздравляет',
    )
    is_congratulate = models.BooleanField(
        'Поздравлять ли пользователя',
        null=False,
        blank=False,
        default=True,
    )
    name = models.CharField(
        'Как называет пользователя',
        max_length=CONSTANTS['MAX_NAME_USER'],
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'subscribe'],
                name='unique_subscriptions'
            ),
        ]

    def __str__(self) -> str:
        return (f'{self.user} поздравляет пользователя {self.subscribe}')

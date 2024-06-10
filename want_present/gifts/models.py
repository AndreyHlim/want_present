from constants import CONSTANTS
from holidays.models import Holiday

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Gift(models.Model):
    """Модель 'Подарки'."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    hyperlink = models.TextField('Ссылка на пример подарка',)
    short_name = models.CharField(
        'Краткое название подарка',
        max_length=CONSTANTS['MAX_NAME_GIFT'],
    )
    is_donated = models.BooleanField('Уже подарен', default=False,)
    is_booked = models.BooleanField('Забронирован к покупке', default=False,)
    is_want = models.BooleanField('Хочет подарок', default=True,)
    event = models.ForeignKey(
        Holiday,
        on_delete=models.CASCADE,
        verbose_name='Что празднует',
        related_name='gifts',
    )
    comment = models.CharField(
        'Комментарий, желающего',
        max_length=CONSTANTS['MAX_COMMENT'],
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Подарок'
        verbose_name_plural = 'Подарки'

    def __str__(self) -> str:
        return self.short_name[:CONSTANTS['MAX_NAME_GIFT_ADMIN']]

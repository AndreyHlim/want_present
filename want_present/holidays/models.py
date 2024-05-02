from django.db import models
from django.contrib.auth import get_user_model
from constants import CONSTANTS


User = get_user_model()


class Holiday(models.Model):
    """Модель 'Праздники'."""

    name = models.CharField(
        'Название праздника',
        max_length=CONSTANTS['MAX_NAME_HOLIDAY'],
    )
    date = models.DateField('Дата праздника',)
    user = models.ForeignKey(
        User,
        verbose_name='Чей праздник',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Праздник'
        verbose_name_plural = 'Праздники'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'date', 'name'],
                name='unique_holidays',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.date}_{self.name}_у id: {self.user}'

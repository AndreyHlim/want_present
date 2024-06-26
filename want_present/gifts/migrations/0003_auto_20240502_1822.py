# Generated by Django 3.2.16 on 2024-05-02 18:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('holidays', '0004_holiday_unique_holidays'),
        ('gifts', '0002_auto_20240428_2001'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gift',
            old_name='link',
            new_name='hyperlink',
        ),
        migrations.AddField(
            model_name='gift',
            name='comment',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Комментарий, желающего'),
        ),
        migrations.AddField(
            model_name='gift',
            name='event',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='holidays.holiday'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gift',
            name='is_booked',
            field=models.BooleanField(default=False, verbose_name='Забронирован к покупке'),
        ),
        migrations.AlterField(
            model_name='gift',
            name='is_donated',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='gift',
            name='is_want',
            field=models.BooleanField(default=True, verbose_name='Хочет подарок'),
        ),
        migrations.AlterField(
            model_name='gift',
            name='short_name',
            field=models.CharField(max_length=100, verbose_name='Краткое название подарка'),
        ),
    ]

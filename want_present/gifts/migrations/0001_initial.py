# Generated by Django 3.2.16 on 2024-04-28 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Gift',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_name', models.CharField(max_length=50, verbose_name='Краткое название подарка')),
                ('link', models.TextField(verbose_name='Ссылка на покупку подарка')),
            ],
        ),
    ]

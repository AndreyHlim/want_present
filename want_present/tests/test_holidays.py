from datetime import datetime, timedelta

import pytest
from constants import CONSTANTS
from holidays.models import Holiday
from rest_framework import status


@pytest.mark.parametrize(
    'client_user, answer',
    [
        (pytest.lazy_fixture('author_client'), status.HTTP_200_OK),
        (pytest.lazy_fixture('not_author_client'), status.HTTP_200_OK),
        (pytest.lazy_fixture('client'), status.HTTP_401_UNAUTHORIZED),
    ]
)
def test_pages_availability_for_user(client_user, url_holiday, answer):
    """Проверяет доступен ли конерктный праздник любому авторизованному user"""
    response = client_user.get(url_holiday)
    assert response.status_code == answer


@pytest.mark.parametrize(
    'client_user, answer, name',
    [
        (
            pytest.lazy_fixture('author_client'),
            status.HTTP_200_OK,
            'Изменённое название праздника'
        ),
        (
            pytest.lazy_fixture('not_author_client'),
            status.HTTP_403_FORBIDDEN,
            'Тестовый праздник'
        ),
        (
            pytest.lazy_fixture('client'),
            status.HTTP_401_UNAUTHORIZED,
            'Тестовый праздник'
        ),
    ],
    ids=['author', 'not author', 'not_auth_user'],
)
def test_change_name_holiday_for_user(client_user, answer, url_holiday, name):
    """Проверяет возможность изменения имени праздника только его автору"""
    response = client_user.patch(
        path=url_holiday,
        data={'name': 'Изменённое название праздника'},
        format='json'
    )
    assert response.status_code == answer, (
        'Убедитель в том, что данные о празднике '
        'может изменять автор (только автор) праздника.'
    )
    new_holiday = Holiday.objects.get()
    assert new_holiday.name == name, (
        'Убедитесь в том, что ПРОИСХОДИТ изменение названия праздника '
        'в базе данных, если его изменяет АВТОР и НЕ ИЗМЕНЯЕТСЯ название '
        'праздника, если это пытается сделать другой пользователь.'
    )


def test_del_holiday_for_author(author_client, url_holiday):
    """Проверяет позможность удаления праздника только его автором"""

    response = author_client.delete(url_holiday)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Holiday.objects.count() == 0


def test_del_holiday_for_not_author(not_author_client, url_holiday):
    not_author_client.delete(url_holiday)
    assert Holiday.objects.count() == 1


def test_holiday_without_name(holiday_data, author_client, author):
    holiday_data.pop('name')
    response = author_client.post(
        path='/api/holidays/',
        data={
            'date': '2034-05-22',
            'user': author.id_telegram
        },
        format='json'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST, (
        'Убедитесь в том, что при создании праздника передано значение "name"'
    )


def test_holiday_long_name(holiday_data, author_client, author):
    holiday_data['name'] = CONSTANTS['MAX_NAME_HOLIDAY']*'O'+'P'
    holiday_data['user'] = author.id_telegram
    response = author_client.post(
        path='/api/holidays/',
        data=holiday_data,
        format='json'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST, (
        'Убедитесь в том, что поле "name" для создаваемого праздника '
        'не длинее {0} символов.'.format(CONSTANTS['MAX_NAME_HOLIDAY'])
    )


def test_holiday_without_date(holiday_data, author_client, author):
    holiday_data.pop('date')
    response = author_client.post(
        '/api/holidays/',
        data={'name': 'какой-то праздник', 'user': author.id_telegram},
        format='json'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST, (
        'Убедитесь в том, что при создании праздника передано значение "date".'
    )


def test_repeat_holiday(author_client, holiday):
    before_count = Holiday.objects.count()
    response = author_client.post(
        path='/api/holidays/',
        data={
            'name': holiday.name,
            'date': holiday.date,
            'user': holiday.user.id_telegram
        },
        format='json'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST, (
        'Убедитесь в том, что невозможно создать два праздника '
        'с одинаковыми "name", "date" и "user".'
    )
    assert before_count == Holiday.objects.count(), (
        'Убедитесь в том, что при некорректных данных о празднике '
        '(попытка повторного сохранения праздника) '
        'в базе не создаётся новыая запись.'
    )


def test_holiday_past_date(author_client, holiday_data, author):
    before_count = Holiday.objects.count()
    holiday_data['user'] = author.id_telegram
    response = author_client.post(
        path='/api/holidays/',
        data={
            'name': holiday_data['name'],
            'date': datetime.now().date() - timedelta(days=1),
            'user': holiday_data['user']
        },
        format='json'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST, (
        'Убедитесь в том, что невозможно '
        'при создании ближайшего дня празднования '
        'указать прошедшую дату.'
    )
    assert before_count == Holiday.objects.count()

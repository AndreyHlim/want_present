from datetime import datetime, timedelta

import pytest
from constants import CONSTANTS
from holidays.models import Holiday
from rest_framework import status


@pytest.mark.parametrize(
    'client_user, answer',
    [
        (pytest.lazy_fixture('admin_client'), status.HTTP_200_OK),
        (pytest.lazy_fixture('author_client'), status.HTTP_200_OK),
        (pytest.lazy_fixture('not_author_client'), status.HTTP_200_OK),
        (pytest.lazy_fixture('client'), status.HTTP_401_UNAUTHORIZED),
    ]
)
def test_pages_availability_for_user(client_user, url_holiday, answer):
    """Проверяет доступен ли конкретный праздник любому авторизованному user"""
    response = client_user.get(url_holiday)
    assert response.status_code == answer, (
        'Убедитесь, что авторизованные пользователи имею доступ '
        'к отбельному празднику, а неавторизованные - нет'
    )


@pytest.mark.parametrize(
    'client_user, answer, name',
    [
        (
            pytest.lazy_fixture('admin_client'),
            status.HTTP_200_OK,
            'Изменённое название'
        ),
        (
            pytest.lazy_fixture('author_client'),
            status.HTTP_200_OK,
            'Изменённое название'
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
    ids=['admin', 'author', 'not author', 'not_auth_user'],
)
def test_change_name_holiday_for_user(client_user, answer, url_holiday, name):
    """Проверяет возможность изменения имени праздника только его автору"""
    response = client_user.patch(url_holiday, {'name': 'Изменённое название'})
    assert response.status_code == answer, (
        'Убедитель в том, что данные о празднике '
        'может изменять автор (только автор) праздника'
    )
    new_holiday = Holiday.objects.get()
    assert new_holiday.name == name, (
        'Убедитесь в том, что ПРОИСХОДИТ изменение названия праздника '
        'в базе данных, если его изменяет АВТОР и НЕ ИЗМЕНЯЕТСЯ название '
        'праздника, если это пытается сделать другой пользователь'
    )


def test_del_holiday_for_author(author_client, url_holiday):
    """Проверяет возможность удаления праздника только его автором"""
    response = author_client.delete(url_holiday)
    assert response.status_code == status.HTTP_204_NO_CONTENT, (
        'Убедитесь в том, что пользователь может удалить свой праздник'
    )
    assert Holiday.objects.count() == 0, (
        'Убедитесь в том, что пользователь может удалить свой праздник'
    )


def test_del_holiday_for_not_author(not_author_client, url_holiday):
    """Проверяет невозможность удаления праздника не его автором"""
    response = not_author_client.delete(url_holiday)
    message = 'Убедитесь в том, что праздник может удалить только его автор'
    assert response.status_code == status.HTTP_403_FORBIDDEN, message
    assert Holiday.objects.count() == 1, message


def test_holiday_without_name(author_client, url_holidays, holiday_data):
    """Проверяет невозможность создания праздника без указания названия"""
    holiday_data.pop('name')
    response = author_client.post(url_holidays, {**holiday_data}, 'json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST, (
        'Убедитесь в том, что при создании праздника передано значение "name"'
    )


def test_holiday_long_name(holiday_data, author_client, url_holidays):
    """Проверяет ограничение длины имени праздника"""
    holiday_data['name'] = CONSTANTS['MAX_NAME_HOLIDAY']*'O'+'P'
    response = author_client.post(url_holidays, {**holiday_data}, 'json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST, (
        'Убедитесь в том, что поле "name" для создаваемого праздника '
        'не длинее {0} символов.'.format(CONSTANTS['MAX_NAME_HOLIDAY'])
    )


def test_holiday_without_date(author_client, url_holidays, holiday_data):
    """Проверяет невозможность создания праздника без указания даты"""
    holiday_data.pop('date')
    response = author_client.post(url_holidays, {**holiday_data}, 'json')
    print(response.data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST, (
        'Убедитесь в том, что при создании праздника передано значение "date".'
    )


def test_repeat_holiday(
    author_client, holiday, author, url_holidays, holiday_data
):
    """Проверяет невозможность сохранения двух одинаковых праздников"""
    before_count = Holiday.objects.count()
    holiday_data['user'] = author.id_telegram
    response = author_client.post(url_holidays, {**holiday_data}, 'json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST, (
        'Убедитесь в том, что невозможно создать два праздника '
        'с одинаковыми "name", "date" и "user".'
    )
    assert before_count == Holiday.objects.count(), (
        'Убедитесь в том, что при некорректных данных о празднике '
        '(попытка повторного сохранения праздника) '
        'в базе не создаётся новыая запись.'
    )


@pytest.mark.parametrize(
    'dt',
    [
        datetime.now().date() - timedelta(days=1),
        datetime.now().date().replace(
            year=datetime.now().date().year+CONSTANTS['LIFE_SPAN']
        ),
    ],
    ids=['past', 'life span'],
)
def test_holiday_wrong_date(author_client, holiday_data, dt, url_holidays):
    """
    Проверяет невозможность создания ближайшей даты празднования праздника:
    1) в прошедшем времени;
    2) далеко в будущем.
    """
    holiday_data['date'] = dt
    before_count = Holiday.objects.count()
    response = author_client.post(url_holidays, {**holiday_data}, 'json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST, (
        'Убедитесь в том, что невозможно '
        'при создании ближайшего дня празднования '
        'указать прошедшую дату или дату в далёком будущем.'
    )
    assert before_count == Holiday.objects.count(), (
        'Убедитесь в том, что при некорректной дате праздника '
        '(в прошлом или сильно в будущем) не создаётся новая запись в базе'
    )


def test_holiday_wrong_user(author_client, author, url_holidays, holiday_data):
    """Проверяет невозможность создания праздника без указания даты"""
    holiday_data['name'] = 'какая-то длинная непонятная строка вместо User'
    response = author_client.post(url_holidays, {**holiday_data}, 'json')
    message = 'Убедитесь в том, что праздник создаётся от имени запрашивающего'
    assert response.status_code == status.HTTP_201_CREATED, message
    holiday = Holiday.objects.get()
    assert holiday.user == author, message

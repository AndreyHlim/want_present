from datetime import datetime, timedelta

import pytest
from constants import CONSTANTS
from holidays.models import Holiday


def test_pages_availability_for_author(author_client, holiday):
    url = f'/api/holidays/{holiday.id}/'
    response = author_client.get(url)
    assert response.status_code == 200


def test_pages_availability_for_not_author(not_author_client, holiday):
    url = f'/api/holidays/{holiday.id}/'
    response = not_author_client.get(url)
    assert response.status_code == 200


def test_change_holiday_for_author(author_client, holiday):
    new_name = 'Изменённое название праздника'
    author_client.patch(
        path=f'/api/holidays/{holiday.id}/',
        data={'name': new_name},
        format='json'
    )
    new_holiday = Holiday.objects.get()
    assert new_holiday.name == new_name


def test_change_holiday_for_not_author(not_author_client,
                                       holiday,
                                       holiday_data):
    old_name = holiday.name
    new_name = 'Изменённое название праздника'
    response = not_author_client.patch(
        path=f'/api/holidays/{holiday.id}/',
        data={'name': new_name},
        format='json'
    )
    new_holiday = Holiday.objects.get()
    assert response.status_code == 403
    assert new_holiday.name == old_name


@pytest.mark.django_db
def test_count_holidays_db():
    assert Holiday.objects.count() == 0


@pytest.mark.django_db
def test_count_holidays_db_1(holiday):
    assert Holiday.objects.count() == 1


def test_del_holiday_for_author(author_client, holiday):
    url = f'/api/holidays/{holiday.id}/'
    response = author_client.delete(url)
    assert response.status_code == 204
    assert Holiday.objects.count() == 0


def test_del_holiday_for_not_author(not_author_client, holiday):
    url = f'/api/holidays/{holiday.id}/'
    not_author_client.delete(url)
    assert Holiday.objects.count() == 1


def test_holiday_without_name(holiday_data, author_client, author):
    holiday_data.pop('name')
    response = author_client.post(
        '/api/holidays/',
        data={'date': '2034-05-22', 'user': author.id_telegram},
        format='json'
    )
    assert response.status_code == 400, (
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
    assert response.status_code == 400, (
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
    assert response.status_code == 400, (
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
    assert response.status_code == 400, (
        'Убедитесь в том, что невозможно создать два праздника '
        'с одинаковыми "name", "date" и "user".'
    )
    assert before_count == Holiday.objects.count()


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
    assert response.status_code == 400, (
        'Убедитесь в том, что невозможно '
        'при создании ближайшего дня празднования '
        'указать прошедшую дату.'
    )
    assert before_count == Holiday.objects.count()

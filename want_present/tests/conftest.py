import pytest
from gifts.models import Gift
from holidays.models import Holiday
from rest_framework.test import APIClient

from django.urls import reverse


@pytest.fixture
def admin(django_user_model, user_data):
    return django_user_model.objects.create_superuser(**user_data['admin'])


@pytest.fixture
def admin_client(client, admin, url_login, user_data):
    response = client.post(url_login, {**user_data['admin']})
    token = response.data['auth_token']
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return client


@pytest.fixture
def author(django_user_model, user_data):
    user = django_user_model.objects.create(**user_data['author'])
    user.set_password(user_data['author']['password'])
    user.save()
    return user


@pytest.fixture
def author_client(client, url_login, author, user_data):
    response = client.post(url_login, {**user_data['author']})
    token = response.data['auth_token']
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return client


@pytest.fixture
def holiday(holiday_data, author):
    holiday_data['user'] = author
    holiday = Holiday.objects.create(**holiday_data)
    return holiday


@pytest.fixture
def not_author_client(client, django_user_model, url_login, user_data):
    user = django_user_model.objects.create(**user_data['not_author'])
    user.set_password(user_data['not_author']['password'])
    user.save()
    response = client.post(url_login, {**user_data['not_author']})
    token = response.data['auth_token']
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return client


@pytest.fixture
def url_holiday(holiday):
    return reverse('api:holidays-detail', kwargs={"pk": holiday.id})


@pytest.fixture
def url_holidays():
    return reverse('api:holidays-list')


@pytest.fixture
def url_users():
    return reverse('api:users-list')


@pytest.fixture
def url_login():
    return reverse('login')


@pytest.fixture
def url_holidays_author(author):
    url_user = reverse('api:users-detail', kwargs={"pk": author.id_telegram})
    return url_user + 'holidays/'


@pytest.fixture
def user_data():
    return {
        'admin': {
            'id_telegram': 777777777,
            'username': 'Admin',
            'email': 'admin@admin.admin',
            'password': '1234567890',
        },
        'author': {
            'id_telegram': 666666666,
            'username': 'Author',
            'password': '1234567890',
        },
        'not_author': {
            'id_telegram': 555555555,
            'username': 'Not_Author',
            'password': '1234567890',
        },
    }


@pytest.fixture
def holiday_data():
    return {
        'name': 'Тестовый праздник',
        'date': '2033-09-04',
    }


@pytest.fixture
def gift_data(holiday):
    return {
        'short_name': 'Какое-то название',
        'hyperlink': 'Какая-то ссылка',
        'event': holiday,
        'comment': 'Комментарий к подарку',
        'user': holiday.user,
    }


@pytest.fixture
def gift(gift_data):
    gift = Gift.objects.create(**gift_data)
    return gift


@pytest.fixture
def url_gift(gift):
    return reverse('api:gifts-detail', kwargs={'pk': gift.id})

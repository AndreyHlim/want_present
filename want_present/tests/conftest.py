import pytest
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
def holiday(author):
    holiday = Holiday.objects.create(
        name='Тестовый праздник',
        date='2033-09-04',
        user=author,
    )
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
def url_login():
    return reverse('login')


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

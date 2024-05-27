import pytest
from holidays.models import Holiday
from rest_framework.test import APIClient

from django.urls import reverse


@pytest.fixture
def admin(django_user_model):
    return django_user_model.objects.create_superuser(
        id_telegram=777777777,
        username='Admin',
        password='1234567890',
        email='admin@admin.admin'
    )


@pytest.fixture
def admin_client(client, admin, url_login):
    response = client.post(
        path=url_login,
        data={
            'id_telegram': admin.id_telegram,
            'password': '1234567890',
        },
        format='json'
    )
    admin_token = response.data['auth_token']
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + admin_token)
    return client


@pytest.fixture
def author(django_user_model):
    user = django_user_model.objects.create(
        id_telegram=123456789,
        username='Author',
    )
    user.set_password('1234567890')
    user.save()
    return user


@pytest.fixture
def author_client(client, url_login, author):
    response = client.post(
        path=url_login,
        data={
            'id_telegram': author.id_telegram,
            'password': '1234567890',
        },
        format='json'
    )
    author_token = response.data['auth_token']
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + author_token)
    return client


@pytest.fixture
def holiday(author):
    holiday = Holiday.objects.create(
        name='Тестовый праздник',
        date='2033-09-04',
        user=author
    )
    return holiday


@pytest.fixture
def not_author_user_data():
    return {
        'id_telegram': 444444444,
        'username': 'Not_author',
        'password': '123456',
    }


@pytest.fixture
def not_author(django_user_model, not_author_user_data):
    return django_user_model.objects.create_superuser(**not_author_user_data)


@pytest.fixture
def not_author_token(client, not_author, not_author_user_data, url_login):
    response = client.post(url_login, not_author_user_data, format='json')
    return response.data['auth_token']


@pytest.fixture
def not_author_client(not_author_token):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + not_author_token)
    return client


@pytest.fixture
def url_holiday(holiday):
    return reverse('api:holidays-detail', kwargs={"pk": holiday.id})


@pytest.fixture
def url_login():
    return reverse('login')

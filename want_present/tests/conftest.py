import pytest
from rest_framework.test import APIClient


@pytest.fixture
def admin_user_data():
    return {
        'id_telegram': 777777777,
        'username': 'Admin',
        'is_superuser': True,
        'is_staff': True,
        'password': '1234567890',
        'email': 'admin@admin.admin'
    }


@pytest.fixture
def admin_user(django_user_model, admin_user_data):
    return django_user_model.objects.create_superuser(**admin_user_data)


@pytest.fixture
def admin_token(client, admin_user, admin_user_data):
    login_url = '/auth/token/login/'
    response = client.post(login_url, admin_user_data, format='json')
    return response.data['auth_token']


@pytest.fixture
def admin_client(admin_token):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + admin_token)
    return client


@pytest.fixture
def author_user_data():
    return {
        'id_telegram': 123456789,
        'username': 'Author',
        'password': '1234567890',
    }


@pytest.fixture
def author(django_user_model, author_user_data):
    return django_user_model.objects.create_superuser(**author_user_data)


@pytest.fixture
def author_token(client, author, author_user_data):
    login_url = '/auth/token/login/'
    response = client.post(login_url, author_user_data, format='json')
    return response.data['auth_token']


@pytest.fixture
def author_client(author_token):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + author_token)
    return client

import pytest
from rest_framework import status


@pytest.mark.parametrize(
    'client_user, url, answer',
    [
        (
            pytest.lazy_fixture('admin_client'),
            pytest.lazy_fixture('url_holidays'),
            status.HTTP_200_OK,
        ),
        (
            pytest.lazy_fixture('author_client'),
            pytest.lazy_fixture('url_holidays'),
            status.HTTP_200_OK,
        ),
        (
            pytest.lazy_fixture('client'),
            pytest.lazy_fixture('url_holidays'),
            status.HTTP_401_UNAUTHORIZED,
        ),
        (
            pytest.lazy_fixture('client'),
            pytest.lazy_fixture('url_users'),
            status.HTTP_401_UNAUTHORIZED,
        ),
        (
            pytest.lazy_fixture('admin_client'),
            pytest.lazy_fixture('url_users'),
            status.HTTP_200_OK,
        ),
        (
            pytest.lazy_fixture('author_client'),
            pytest.lazy_fixture('url_users'),
            status.HTTP_200_OK,
        ),
        (
            pytest.lazy_fixture('admin_client'),
            pytest.lazy_fixture('url_holidays_author'),
            status.HTTP_200_OK,
        ),
        (
            pytest.lazy_fixture('author_client'),
            pytest.lazy_fixture('url_holidays_author'),
            status.HTTP_200_OK,
        ),
        (
            pytest.lazy_fixture('client'),
            pytest.lazy_fixture('url_holidays_author'),
            status.HTTP_401_UNAUTHORIZED,
        ),
        (
            pytest.lazy_fixture('not_author_client'),
            pytest.lazy_fixture('url_holidays_author'),
            status.HTTP_200_OK,
        ),
    ]
)
def test_access_to_API(client_user, url, answer):
    """Тест проверяющий права доступа."""
    response = client_user.get(url)
    assert response.status_code == answer

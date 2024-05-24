import pytest


@pytest.mark.parametrize(
    'user, url, answer',
    [
        (pytest.lazy_fixture('admin_client'), '/api/holidays/', 200),
        (pytest.lazy_fixture('author_client'), '/api/holidays/', 200),
        (pytest.lazy_fixture('client'), '/api/holidays/', 401),
        (pytest.lazy_fixture('client'), '/api/users/', 401),
        (pytest.lazy_fixture('admin_client'), '/api/users/', 200),
        (pytest.lazy_fixture('author_client'), '/api/users/', 200),
    ]
)
def test_access_to_API(user, url, answer):
    """Тест проверяющий права доступа."""
    response = user.get(url)
    assert response.status_code == answer

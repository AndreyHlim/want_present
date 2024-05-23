import pytest


@pytest.mark.parametrize(
    'user, url, answer',
    [
        (pytest.lazy_fixture('admin_client'), '/api/holidays/', 200),
        (pytest.lazy_fixture('author_client'), '/api/holidays/', 200),
        (pytest.lazy_fixture('client'), '/api/holidays/', 401)
    ]
)
def test_with_admin_client(user, url, answer):
    """Тест проверяющий права доступа."""
    response = user.get(url)
    assert response.status_code == answer

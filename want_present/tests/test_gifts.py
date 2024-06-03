import pytest
from rest_framework import status


@pytest.mark.parametrize(
    'client_user, answer',
    [
        (pytest.lazy_fixture('admin_client'), status.HTTP_204_NO_CONTENT),
        (pytest.lazy_fixture('author_client'), status.HTTP_204_NO_CONTENT),
        (pytest.lazy_fixture('not_author_client'), status.HTTP_403_FORBIDDEN),
        (pytest.lazy_fixture('client'), status.HTTP_401_UNAUTHORIZED),
    ]
)
def test_del_gift_another_user(client_user, answer, url_gift):
    response = client_user.delete(url_gift)
    assert response.status_code == answer


@pytest.mark.parametrize(
    'client_user, answer',
    [
        (pytest.lazy_fixture('admin_client'), status.HTTP_200_OK),
        (pytest.lazy_fixture('author_client'), status.HTTP_200_OK),
        (pytest.lazy_fixture('not_author_client'), status.HTTP_403_FORBIDDEN),
        (pytest.lazy_fixture('client'), status.HTTP_401_UNAUTHORIZED),
    ]
)
def test_change_short_name_gift(gift, client_user, url_gift, answer):
    response = client_user.patch(
        url_gift,
        {'short_name': 'Измененное название подарка'},
    )
    assert response.status_code == answer

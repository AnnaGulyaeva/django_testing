from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf


@pytest.mark.django_db
@pytest.mark.parametrize(
    'reverse_url, parametrized_client, status',
    (
        (
            lf('news_home_url'),
            lf('client'),
            HTTPStatus.OK
        ),
        (
            lf('news_detail_url'),
            lf('client'),
            HTTPStatus.OK
        ),
        (
            lf('users_login_url'),
            lf('client'),
            HTTPStatus.OK
        ),
        (
            lf('users_logout_url'),
            lf('client'),
            HTTPStatus.OK
        ),
        (
            lf('users_signup_url'),
            lf('client'),
            HTTPStatus.OK
        ),
        (
            lf('news_edit_url'),
            lf('author_client'),
            HTTPStatus.OK
        ),
        (
            lf('news_edit_url'),
            lf('reader_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            lf('news_delete_url'),
            lf('author_client'),
            HTTPStatus.OK
        ),
        (
            lf('news_delete_url'),
            lf('reader_client'),
            HTTPStatus.NOT_FOUND
        ),
    )
)
def test_availability_for_comment_edit_and_delete(
    reverse_url, parametrized_client, status
):
    """Проверка доступности страниц."""
    response = parametrized_client.get(reverse_url)
    assert response.status_code == status


@pytest.mark.parametrize(
    'reverse_url',
    (
        lf('news_edit_url'),
        lf('news_delete_url')
    )
)
def test_redirect_for_anonymous_client(client, users_login_url, reverse_url):
    """Проверка переадресации."""
    expected_url = f'{users_login_url}?next={reverse_url}'
    response = client.get(reverse_url)
    assertRedirects(response, expected_url)

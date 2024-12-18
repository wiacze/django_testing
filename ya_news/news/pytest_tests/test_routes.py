from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client',
    (
        pytest.lazy_fixture('client'),
        pytest.lazy_fixture('author_client'),
        pytest.lazy_fixture('admin_client'),
    )
)
@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('home_url'),
        pytest.lazy_fixture('login_url'),
        pytest.lazy_fixture('logout_url'),
        pytest.lazy_fixture('signup_url'),
        pytest.lazy_fixture('detail_url'),
    )
)
def test_pages_availability_for_anon_user(parametrized_client, url):
    response = parametrized_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
    ),
)
@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('edit_comment_url'),
        pytest.lazy_fixture('delete_comment_url'),
    ),
)
def test_pages_availability_for_diff_users(
        parametrized_client, url, expected_status
):
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('edit_comment_url'),
        pytest.lazy_fixture('delete_comment_url'),
    ),
)
def test_redirects(url, login_url, client):
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)

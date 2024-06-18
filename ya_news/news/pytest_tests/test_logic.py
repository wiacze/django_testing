from http import HTTPStatus
from random import choice

import pytest
from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from news.pytest_tests.conftest import COMMENT_TEXT
from pytest_django.asserts import assertFormError, assertRedirects

NEW_COMMENT_TEXT = 'Новый текст комментария'
form_data = {'text': NEW_COMMENT_TEXT}


def comments_before_request():
    return Comment.objects.count()


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(detail_url, client):
    COMMENTS_BEFORE_REQUEST = comments_before_request()
    client.post(detail_url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == COMMENTS_BEFORE_REQUEST


@pytest.mark.django_db
def test_user_can_create_comment(detail_url, admin_client):
    COMMENTS_BEFORE_REQUEST = comments_before_request()
    response = admin_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == COMMENTS_BEFORE_REQUEST + 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']


@pytest.mark.django_db
def test_user_cant_use_bad_words(detail_url, admin_client):
    COMMENTS_BEFORE_REQUEST = comments_before_request()
    bad_words_data = {'text': f'Текст, {choice(BAD_WORDS)}, еще текст'}
    response = admin_client.post(detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == COMMENTS_BEFORE_REQUEST


@pytest.mark.django_db
def test_author_can_delete_comment(
    delete_comment_url,
    detail_url,
    author_client
):
    COMMENTS_BEFORE_REQUEST = comments_before_request()
    response = author_client.delete(delete_comment_url)
    assertRedirects(response, f'{detail_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == COMMENTS_BEFORE_REQUEST - 1


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(
    delete_comment_url,
    admin_client
):
    COMMENTS_BEFORE_REQUEST = comments_before_request()
    response = admin_client.delete(delete_comment_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == COMMENTS_BEFORE_REQUEST


@pytest.mark.django_db
def test_author_can_edit_comment(
    edit_comment_url,
    detail_url,
    comment,
    author_client
):
    response = author_client.post(edit_comment_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
    edit_comment_url,
    comment,
    admin_client
):
    response = admin_client.post(edit_comment_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT

import pytest
from django.conf import settings


@pytest.mark.django_db
def test_news_count(more_news, home_url, client):
    response = client.get(home_url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(more_news, home_url, client):
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(comments, detail_url, client):
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    for i in range(all_comments.count() - 1):
        if all_comments[i].created > all_comments[i + 1].created:
            assert False, 'Некорректная сортировка комментариев'


@pytest.mark.django_db
def test_anon_client_has_no_form(detail_url, client):
    response = client.get(detail_url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_auth_client_has_form(detail_url, author_client):
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert type(response.context['form']).__name__ == 'CommentForm'

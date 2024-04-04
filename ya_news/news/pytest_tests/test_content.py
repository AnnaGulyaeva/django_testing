import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


pytestmark = pytest.mark.django_db


def test_news_count(client, news_home_url, all_news):
    """Проверка количества новостей на главной странице."""
    response = client.get(news_home_url)
    news_count = response.context['object_list'].count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, news_home_url, all_news):
    """Проверка порядка сортировки новостей."""
    response = client.get(news_home_url)
    all_dates = [news.date for news in response.context['object_list']]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, news_detail_url, comments):
    """Проверка порядка сортировки комментариев."""
    response = client.get(news_detail_url)
    assert 'news' in response.context
    news_data = response.context['news']
    all_comments = news_data.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestanps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestanps


def test_anonymous_client_has_no_form(client, news_detail_url):
    """Проверка формы комментария для анонимного пользователя."""
    response = client.get(news_detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, news_detail_url):
    """Проверка формы комментария для авторизованного пользователя."""
    response = author_client.get(news_detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)

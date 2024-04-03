import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, all_news):
    """Проверка количества новостей на главной странице."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, all_news):
    """Проверка порядка сортировки новостей."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, news, comments):
    """Проверка порядка сортировки комментариев."""
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'news' in response.context
    news_data = response.context['news']
    all_comments = news_data.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestanps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestanps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news):
    """Проверка формы комментария для анонимного пользователя."""
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, news):
    """Проверка формы комментария для авторизованного пользователя."""
    url = reverse('news:detail', args=(news.id,))
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)

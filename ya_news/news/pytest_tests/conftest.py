from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    """Фикстура автора."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model):
    """Фикстура читателя."""
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author):
    """Фикстура клиента автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    """Фикстура клиента читателя."""
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news():
    """Фикстура объекта новости."""
    news = News.objects.create(
        title='Заголовок',
        text='Текст'
    )
    return news


@pytest.fixture
def all_news(scope="module"):
    """Фикстура списка объектов новостей."""
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def comment(author, news):
    """Фикстура объекта комментария."""
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def comments(author, news, scope="module"):
    """Фикстура списка объектов комментариев."""
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def news_home_url():
    """Фикстура url главной страницы."""
    return reverse('news:home')


@pytest.fixture
def news_detail_url(news):
    """Фикстура url страницы новости."""
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def news_edit_url(comment):
    """Фикстура url редактирования комментария."""
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def news_delete_url(comment):
    """Фикстура url удаления комментария."""
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def users_login_url():
    """Фикстура url аутентификации пользователя."""
    return reverse('users:login')


@pytest.fixture
def users_logout_url():
    """Фикстура url выхода пользователя."""
    return reverse('users:logout')


@pytest.fixture
def users_signup_url():
    """Фикстура url регистрации пользователя."""
    return reverse('users:signup')

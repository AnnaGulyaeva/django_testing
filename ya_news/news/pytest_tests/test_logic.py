import pytest
from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymus_user_cant_create_comment(client, news, form_data):
    """Проверка отправки комментария анонимным пользователем."""
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=form_data)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(reader_client, reader, news, form_data):
    """Проверка отправки комментария авторизованным пользователем."""
    url = reverse('news:detail', args=(news.id,))
    response = reader_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == reader


def test_user_cant_use_bad_words(reader_client, news):
    """Проверка блокировки стоп-слов."""
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = reader_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment):
    """Проверка удаления своего комментария."""
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.post(url)
    news_url = reverse('news:detail', args=(comment.news.id,))
    assertRedirects(response, f'{news_url}#comments')
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(reader_client, comment):
    """Проверка удаления чужого комментария."""
    url = reverse('news:delete', args=(comment.id,))
    response = reader_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(author_client, comment, form_data):
    """Проверка редактирования своего комментария."""
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, form_data)
    news_url = reverse('news:detail', args=(comment.news.id,))
    assertRedirects(response, f'{news_url}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
    comment, reader_client, form_data
):
    """Проверка редактирования чужого комментария."""
    url = reverse('news:edit', args=(comment.id,))
    response = reader_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != form_data['text']

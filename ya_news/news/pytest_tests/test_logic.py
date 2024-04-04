from http import HTTPStatus
from random import choice

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


NEW_COMMENT = {'text': 'Обновлённый комментарий'}


@pytest.mark.django_db
def test_anonymus_user_cant_create_comment(client, news_detail_url):
    """Проверка отправки комментария анонимным пользователем."""
    comments_count = Comment.objects.count()
    client.post(news_detail_url, data=NEW_COMMENT)
    assert Comment.objects.count() == comments_count


def test_user_can_create_comment(reader_client, reader, news, news_detail_url):
    """Проверка отправки комментария авторизованным пользователем."""
    comments_count = Comment.objects.count()
    response = reader_client.post(news_detail_url, data=NEW_COMMENT)
    assertRedirects(response, f'{news_detail_url}#comments')
    assert Comment.objects.count() == comments_count + 1
    comment = Comment.objects.last()
    assert comment.text == NEW_COMMENT['text']
    assert comment.news == news
    assert comment.author == reader


def test_user_cant_use_bad_words(reader_client, news_detail_url):
    """Проверка блокировки стоп-слов."""
    bad_words_data = {
        'text': f'Какой-то текст, {choice(BAD_WORDS)}, еще текст'
    }
    comments_count = Comment.objects.count()
    response = reader_client.post(news_detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == comments_count


@pytest.mark.django_db
def test_author_can_delete_comment(
    author_client, news_delete_url, news_detail_url
):
    """Проверка удаления своего комментария."""
    comments_count = Comment.objects.count()
    response = author_client.post(news_delete_url)
    assertRedirects(response, f'{news_detail_url}#comments')
    assert Comment.objects.count() == comments_count - 1


def test_user_cant_delete_comment_of_another_user(
    reader_client, news_delete_url
):
    """Проверка удаления чужого комментария."""
    comments_count = Comment.objects.count()
    response = reader_client.delete(news_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_count


def test_author_can_edit_comment(
    author_client, author, comment, news, news_edit_url, news_detail_url
):
    """Проверка редактирования своего комментария."""
    response = author_client.post(news_edit_url, NEW_COMMENT)
    assertRedirects(response, f'{news_detail_url}#comments')
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_edit_comment_of_another_user(
    reader_client, reader, news_edit_url, comment
):
    """Проверка редактирования чужого комментария."""
    response = reader_client.post(news_edit_url, data=NEW_COMMENT)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment = Comment.objects.get(id=comment.id)
    assert comment.text != NEW_COMMENT['text']
    assert comment.author != reader

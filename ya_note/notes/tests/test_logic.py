from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from django.urls import reverse

User = get_user_model()


class TestNoteCreation(TestCase):
    """Тесты отправки записей и корректности slug."""

    NOTE_TITLE = 'Заголовок'
    NOTE_TEXT = 'Текст записи'
    NOTE_SLUG = 'note-slug'

    @classmethod
    def setUpTestData(cls):
        """Создание транзакций для временой базы данных."""
        cls.add_url = reverse('notes:add')
        cls.success_url = reverse('notes:success')
        cls.login_url = reverse('users:login')
        cls.author = User.objects.create(username='Автор')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG
        }

    def test_user_can_create_note(self):
        """Проверка создания записи вторизованным пользователем."""
        response = self.auth_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.author, self.author)
        self.assertEqual(note.slug, self.NOTE_SLUG)

    def test_anonymous_user_cant_create_note(self):
        """Проверка создания заметки анонимным пользователем."""
        response = self.client.post(self.add_url, data=self.form_data)
        expected_url = f'{self.login_url}?next={self.add_url}'
        self.assertRedirects(response, expected_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_empty_slug(self):
        """Проверка создания пустого slug."""
        self.form_data.pop('slug')
        response = self.auth_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteUniqSlug(TestCase):
    """Тесты slug."""

    @classmethod
    def setUpTestData(cls):
        """Создание транзакций для временой базы данных."""
        cls.add_url = reverse('notes:add')
        cls.success_url = reverse('notes:success')
        cls.login_url = reverse('users:login')
        cls.author = User.objects.create(username='Автор')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )
        cls.form_data = {
            'title': 'Заголовок 2',
            'text': 'Текст записи',
            'slug': 'note-slug'
        }

    def test_not_unique_slug(self):
        """Проверка создания двух заметок с одинаковым slug."""
        self.form_data['slug'] = self.note.slug
        response = self.auth_client.post(self.add_url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.note.slug + WARNING
        )
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)


class TestNoteEditDelete(TestCase):
    """Тесты удаления и редактирования записи."""

    NOTE_TITLE = 'Заголовок'
    NOTE_TEXT = 'Текст записи'
    NEW_NOTE_TITLE = 'Обновлённый заголовок'
    NEW_NOTE_TEXT = 'Обновлённый текст записи'
    NEW_NOTE_SLUG = 'Обновлённый slug'

    @classmethod
    def setUpTestData(cls):
        """Создание транзакций для временой базы данных."""
        cls.author = User.objects.create(username='Автор')
        cls.another = User.objects.create(username='Автор 2')
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')
        cls.form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT
        }

    def test_author_can_edit_note(self):
        """Проверка редактирования заметки авторизованным пользователем."""
        self.client.force_login(self.author)
        response = self.client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])

    def test_other_user_cant_edit_note(self):
        """Проверка редактирования аутентифицированным пользователем."""
        self.client.force_login(self.another)
        response = self.client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)

    def test_author_can_delete_note(self):
        """Проверка удаления заметки авторизованным пользователем."""
        self.client.force_login(self.author)
        response = self.client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        comments_count = Note.objects.count()
        self.assertEqual(comments_count, 0)

    def test_other_user_cant_delete_note(self):
        """Проверка удаления заметки аутентифицированным пользователем."""
        self.client.force_login(self.another)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

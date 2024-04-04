from http import HTTPStatus

from pytils.translit import slugify

from .fixtures import TestNoteBase
from notes.forms import WARNING
from notes.models import Note


class TestNoteCreationSlug(TestNoteBase):
    """Тесты отправки записей и корректности slug."""

    NOTE_TITLE = 'Заголовок'
    NOTE_TEXT = 'Текст записи'
    NOTE_SLUG = 'note-slug'

    @classmethod
    def setUpTestData(cls):
        """Создание транзакций для временой базы данных."""
        super().setUpTestData()
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG
        }

    def test_user_can_create_note(self):
        """Проверка создания записи авторизованным пользователем."""
        notes_count = Note.objects.count()
        response = self.user[0].post(self.ADD_URL, data=self.form_data)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), notes_count + 1)
        note = Note.objects.last()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.author, self.author)
        self.assertEqual(note.slug, self.form_data['slug'])

    def test_anonymous_user_cant_create_note(self):
        """Проверка создания заметки анонимным пользователем."""
        notes_count = Note.objects.count()
        response = self.client.post(self.ADD_URL, data=self.form_data)
        expected_url = f'{self.LOGIN_URL}?next={self.ADD_URL}'
        self.assertRedirects(response, expected_url)
        notes_count = Note.objects.count()
        self.assertEqual(Note.objects.count(), notes_count)

    def test_not_unique_slug(self):
        """Проверка создания двух заметок с одинаковым slug."""
        self.form_data['slug'] = self.note.slug
        note_count = Note.objects.count()
        response = self.user[0].post(self.ADD_URL, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.note.slug + WARNING
        )
        self.assertEqual(Note.objects.count(), note_count)


class TestNoteEditDeleteSlug(TestNoteBase):
    """Тесты проверки пустого slug, удаления и редактирования записи."""

    NEW_NOTE_TITLE = 'Обновлённый заголовок'
    NEW_NOTE_TEXT = 'Обновлённый текст записи'

    @classmethod
    def setUpTestData(cls):
        """Создание транзакций для временой базы данных."""
        super().setUpTestData()
        cls.form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT
        }

    def test_empty_slug(self):
        """Проверка создания пустого slug."""
        note_count = Note.objects.count()
        response = self.user[0].post(self.ADD_URL, data=self.form_data)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), note_count + 1)
        new_note = Note.objects.last()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        """Проверка редактирования заметки авторизованным пользователем."""
        response = self.user[0].post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.author, self.author)

    def test_other_user_cant_edit_note(self):
        """Проверка редактирования аутентифицированным пользователем."""
        response = self.user[1].post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.author, self.author)

    def test_author_can_delete_note(self):
        """Проверка удаления заметки авторизованным пользователем."""
        comments_count = Note.objects.count()
        response = self.user[0].delete(self.delete_url)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), comments_count - 1)

    def test_other_user_cant_delete_note(self):
        """Проверка удаления заметки аутентифицированным пользователем."""
        note_count = Note.objects.count()
        response = self.user[1].delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), note_count)

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestNoteBase(TestCase):
    """Тесты для проверки передачи формы в словаре контекста."""

    ADD_URL = reverse('notes:add')
    LIST_URL = reverse('notes:list')
    SUCCESS_URL = reverse('notes:success')
    HOME_URL = reverse('notes:home')
    LOGIN_URL = reverse('users:login')
    LOGOUT_URL = reverse('users:logout')
    SIGNUP_URL = reverse('users:signup')
    NOTE_TITLE = 'Заголовок'
    NOTE_TEXT = 'Текст записи'

    @classmethod
    def setUpTestData(cls):
        """Создание транзакций для временой базы данных."""
        cls.author = User.objects.create(username='Автор')
        cls.another = User.objects.create(username='Автор 2')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.another_client = Client()
        cls.another_client.force_login(cls.another)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))

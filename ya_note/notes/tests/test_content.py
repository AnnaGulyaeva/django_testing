from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestFormNote(TestCase):
    """Тесты для проверки передачи формы в словаре контекста."""

    ADD_URL = reverse('notes:add')
    LIST_URL = reverse('notes:list')
    NOTES_NUMBER = 5

    @classmethod
    def setUpTestData(cls):
        """Создание транзакций для временой базы данных."""
        cls.author = User.objects.create(username='Автор')
        cls.another = User.objects.create(username='Автор 2')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )

    def test_notes_list_for_different_users(self):
        """Проверка списка заметок для любого пользователя."""
        users_notes_in_list = (
            (self.author, True),
            (self.another, False),
        )
        for user, notes_in_list in users_notes_in_list:
            with self.subTest(user=user):
                self.client.force_login(user)
                response = self.client.get(self.LIST_URL)
                object_list = response.context['object_list']
                self.assertIs(self.note in object_list, notes_in_list)

    def test_authorized_client_has_form(self):
        """Проверка форм для авторизованного пользователя."""
        urls = (
            ('notes:edit', (self.note.slug,)),
            ('notes:add', None)
        )
        self.client.force_login(self.author)
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)

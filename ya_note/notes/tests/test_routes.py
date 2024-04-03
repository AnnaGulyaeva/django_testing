from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """Тесты для проверки маршрутов."""

    @classmethod
    def setUpTestData(cls):
        """Создание транзакций для временой базы данных."""
        cls.author = User.objects.create(username='Автор')
        cls.another = User.objects.create(username='Автор 2')
        cls.user = User.objects.create(username='Пользователь')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )

    def test_pages_availability_for_anonymous_client(self):
        """Проверка доступности страниц для анонимного пользователя.

        Главной, логина, логаута и регистрации.

        """
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup'
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_autentificate_client(self):
        """Проверка доступности страниц для аутентифицированного пользователя.

        Списка заметок, успешного добавления и добавления новой заметки.

        """
        urls = (
            'notes:home',
            'notes:success',
            'notes:add'
        )
        self.client.force_login(self.author)
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_detail_edit_and_delete(self):
        """Проверка доступности страниц.

        Отдельной заметки, редактирования и удаления.

        """
        urls = (
            'notes:detail',
            'notes:edit',
            'notes:delete'
        )
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.another, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in urls:
                with self.subTest(name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Проверка переадресации."""
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:add', None)
        )
        login_url = reverse('users:login')
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

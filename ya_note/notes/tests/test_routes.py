from http import HTTPStatus

from django.contrib.auth import get_user

from notes.tests.fixtures import TestNoteBase


class TestRoutes(TestNoteBase):
    """Тесты для проверки маршрутов."""

    def test_pages_availability_for_anonymous_client(self):
        """Проверка доступности страниц для анонимного пользователя.

        Главной, логина, логаута и регистрации.

        """
        urls = (
            self.HOME_URL,
            self.LOGIN_URL,
            self.LOGOUT_URL,
            self.SIGNUP_URL
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_autentificate_client(self):
        """Проверка доступности страниц для аутентифицированного пользователя.

        Списка заметок, успешного добавления и добавления новой заметки.

        """
        urls = (
            self.HOME_URL,
            self.SUCCESS_URL,
            self.ADD_URL
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_detail_edit_and_delete(self):
        """Проверка доступности страниц.

        Отдельной заметки, редактирования и удаления.

        """
        urls = (
            self.detail_url,
            self.edit_url,
            self.delete_url
        )
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.another_client, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            for url in urls:
                with self.subTest(url=url, user=get_user(user), status=status):
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Проверка переадресации."""
        urls = (
            self.LIST_URL,
            self.SUCCESS_URL,
            self.ADD_URL,
            self.edit_url,
            self.delete_url,
            self.detail_url
        )
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{self.LOGIN_URL}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

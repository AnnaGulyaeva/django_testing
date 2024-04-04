from .fixtures import TestNoteBase
from notes.forms import NoteForm


class TestFormNote(TestNoteBase):
    """Тесты для проверки передачи формы в словаре контекста."""

    NOTES_NUMBER = 5

    def test_notes_list_for_different_users(self):
        """Проверка списка заметок для любого пользователя."""
        users_notes_in_list = (
            (self.user[0], True),
            (self.user[1], False),
        )
        for user, notes_in_list in users_notes_in_list:
            with self.subTest(user=user):
                response = user.get(self.LIST_URL)
                self.assertIs(
                    self.note in response.context['object_list'], notes_in_list
                )

    def test_authorized_client_has_form(self):
        """Проверка форм для авторизованного пользователя."""
        for url in (self.edit_url, self.ADD_URL):
            with self.subTest(url=url):
                response = self.user[0].get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)

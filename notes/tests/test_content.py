from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class TestListPage(TestCase):
    """Класс для тестирования контента."""

    @classmethod
    def setUpTestData(cls):
        """Метод, подготавливающий данные для тестов."""
        cls.author = User.objects.create(username='Автор')
        cls.not_author = User.objects.create(username='Другой пользователь')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст.',
            slug='slug',
            author=cls.author
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.urls = {
            'LIST': reverse('notes:list'),
            'ADD': reverse('notes:add'),
            'EDIT': reverse('notes:edit', args=(cls.note.slug,)),

        }

    def test_notes_list_for_different_users(self):
        """Тест отображения заметок для разных пользователей."""
        user_clients_note_in_list = (
            (self.author_client, True),
            (self.not_author_client, False),
        )
        for user_client, note_in_list in user_clients_note_in_list:
            with self.subTest(user_client=user_client):
                response = user_client.get(self.urls['LIST'])
                object_list = response.context['object_list']
                self.assertEqual((self.note in object_list), note_in_list)

    def test_pages_contain_form(self):
        """Тест присутствия формы на странице."""
        url_keys = (
            'ADD',
            'EDIT'
        )
        for url_key in url_keys:
            with self.subTest(url_key=url_key):
                response = self.author_client.get(self.urls[url_key])
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


class TestNoteCreation(TestCase):
    """Класс для тестирования логики при создании заметок."""

    NOTE_SLUG = 'some_slug'
    NOTE_TEXT = 'Текст'
    NOTE_TITLE = 'Заголовок'

    @classmethod
    def setUpTestData(cls):
        """Метод, подготавливающий данные для тестов."""
        cls.user = User.objects.create(username='Пользователь')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG,
            'title': cls.NOTE_TITLE
        }
        cls.url = reverse('notes:add')
        cls.done_url = reverse('notes:success')

    def test_anonymous_user_cant_create_note(self):
        """Тест создания заметки неавторизованным пользователем."""
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        """Тест создания заметки авторизованным пользователем."""
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, self.done_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.slug, self.NOTE_SLUG)
        self.assertEqual(note.author, self.user)

    def test_user_cant_use_same_slug(self):
        """Тест создания заметки с таким же slug."""
        Note.objects.create(
            title=self.NOTE_TITLE,
            text=self.NOTE_TEXT,
            slug=self.NOTE_SLUG,
            author=self.user
        )
        response = self.auth_client.post(self.url, data=self.form_data)
        form = response.context['form']
        self.assertFormError(
            form=form,
            field='slug',
            errors=f'{self.NOTE_SLUG}{WARNING}'
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)


class TestNoteEditDelete(TestCase):
    """Класс для тестирования логики при изменении и удалении заметки."""

    NOTE_TITLE = 'Заголовок'
    NOTE_TEXT = 'Текст'
    NEW_NOTE_TEXT = 'Обновленный текст'

    @classmethod
    def setUpTestData(cls):
        """Метод, подготавливающий данные для тестов."""
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.another_user = User.objects.create(username='Другой пользователь')
        cls.another_user_client = Client()
        cls.another_user_client.force_login(cls.another_user)

        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author
        )

        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.done_url = reverse('notes:success')
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT
            }

    def test_author_can_delete_note(self):
        """Тест возможности автора удалять заметки."""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.done_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        """Тест невозможности удаления заметки другого пользователя."""
        response = self.another_user_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_author_can_edit_note(self):
        """Тест возможности автора изменять заметку."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.done_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        """Тест невозможности изменять заметку другого пользователя."""
        response = self.another_user_client.post(
            self.edit_url,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)

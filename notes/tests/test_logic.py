from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

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
        cls.urls = {
            'ADD': reverse('notes:add'),
            'DONE': reverse('notes:success')
        }
        cls.url = reverse('notes:add')
        cls.done_url = reverse('notes:success')

    def test_anonymous_user_cant_create_note(self):
        """Тест создания заметки неавторизованным пользователем."""
        notes_count_before = Note.objects.count()
        self.client.post(self.urls['ADD'], data=self.form_data)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_before, notes_count_after)

    def test_user_can_create_note(self):
        """Тест создания заметки авторизованным пользователем."""
        notes_count_before = Note.objects.count()
        response = self.auth_client.post(self.urls['ADD'], data=self.form_data)
        notes_count_after = Note.objects.count()
        self.assertRedirects(response, self.urls['DONE'])
        self.assertNotEqual(notes_count_before, notes_count_after)
        note = Note.objects.latest('id')
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
        notes_count_before = Note.objects.count()
        response = self.auth_client.post(self.urls['ADD'], data=self.form_data)
        notes_count_after = Note.objects.count()
        form = response.context['form']
        self.assertFormError(
            form=form,
            field='slug',
            errors=f'{self.NOTE_SLUG}{WARNING}'
        )
        self.assertEqual(notes_count_before, notes_count_after)

    def test_empty_slug(self):
        """Тест создания заметки с пустым полем slug."""
        self.form_data.pop('slug')
        notes_count_before = Note.objects.count()
        response = self.auth_client.post(self.urls['ADD'], data=self.form_data)
        notes_count_after = Note.objects.count()
        self.assertRedirects(response, self.urls['DONE'])
        self.assertNotEqual(notes_count_before, notes_count_after)
        new_note = Note.objects.latest('id')
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDelete(TestCase):
    """Класс для тестирования логики при изменении и удалении заметки."""

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
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author
        )
        cls.urls = {
            'EDIT': reverse('notes:edit', args=(cls.note.slug,)),
            'DELETE': reverse('notes:delete', args=(cls.note.slug,)),
            'DONE': reverse('notes:success')
        }
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new_slug'
        }

    def test_author_can_delete_note(self):
        """Тест возможности автора удалять заметки."""
        notes_count_before = Note.objects.count()
        response = self.author_client.delete(self.urls['DELETE'])
        notes_count_after = Note.objects.count()
        self.assertRedirects(response, self.urls['DONE'])
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertNotEqual(notes_count_before, notes_count_after)

    def test_user_cant_delete_note_of_another_user(self):
        """Тест невозможности удаления заметки другого пользователя."""
        notes_count_before = Note.objects.count()
        response = self.another_user_client.delete(self.urls['DELETE'])
        notes_count_after = Note.objects.count()
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(notes_count_before, notes_count_after)

    def test_author_can_edit_note(self):
        """Тест возможности автора изменять заметку."""
        response = self.author_client.post(
            self.urls['EDIT'], data=self.form_data
        )
        self.assertRedirects(response, self.urls['DONE'])
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.slug, self.form_data['slug'])
        self.assertEqual(self.note.author, self.author)

    def test_user_cant_edit_note_of_another_user(self):
        """Тест невозможности изменять заметку другого пользователя."""
        response = self.another_user_client.post(
            self.urls['EDIT'],
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        old_note = self.note
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, old_note.text)
        self.assertEqual(self.note.title, old_note.title)
        self.assertEqual(self.note.slug, old_note.slug)
        self.assertEqual(self.note.author, old_note.author)

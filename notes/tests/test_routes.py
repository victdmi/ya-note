from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):
    """Класс для тестирования маршрутов."""

    @classmethod
    def setUpTestData(cls):
        """Метод, подготавливающий данные для тестирования."""
        cls.author = User.objects.create(username='Автор заметки')
        cls.another_user = User.objects.create(username='Другой пользователь')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )
        cls.urls = {
            'HOME': reverse('notes:home'),
            'LOGIN': reverse('users:login'),
            'LOGOUT': reverse('users:logout'),
            'SIGNUP': reverse('users:signup'),
            'EDIT': reverse('notes:edit', args=(cls.note.slug,)),
            'DETAIL': reverse('notes:detail', args=(cls.note.slug,)),
            'DELETE': reverse('notes:delete', args=(cls.note.slug,)),
            'ADD': reverse('notes:add'),
            'LIST': reverse('notes:list'),
            'DONE': reverse('notes:success')
        }

    def test_pages_availability(self):
        """Тест доступности страниц для неавторизованного пользователя."""
        url_keys = (
            'HOME',
            'LOGIN',
            'LOGOUT',
            'SIGNUP'
        )
        for url_key in url_keys:
            with self.subTest(url_key=url_key):
                if url_key == 'LOGOUT':
                    response = self.client.post(self.urls[url_key])
                else:
                    response = self.client.get(self.urls[url_key])
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_edit_detail_delete(self):
        """Тест страниц создания, редактирования, удаления заметки."""
        users_and_statuses = (
            (self.author, HTTPStatus.OK),
            (self.another_user, HTTPStatus.NOT_FOUND)
        )
        url_keys = (
            'EDIT',
            'DETAIL',
            'DELETE'
        )
        for user, status in users_and_statuses:
            self.client.force_login(user)
            for url_key in url_keys:
                with self.subTest(user=user, url_key=url_key):
                    response = self.client.get(self.urls[url_key])
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Тест редиректов для неавторизованных пользователей."""
        login_url = self.urls['LOGIN']
        url_keys = (
            'ADD',
            'LIST',
            'DONE',
            'EDIT',
            'DETAIL',
            'DELETE'
        )
        for url_key in url_keys:
            with self.subTest(url_key=url_key):
                redirect_url = f'{login_url}?next={self.urls[url_key]}'
                response = self.client.get(self.urls[url_key])
                self.assertRedirects(response, redirect_url)

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from notes.models import Note


User = get_user_model()


class TestListPage(TestCase):

    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Пользователь')
        Note.objects.bulk_create(
            Note(
                title='Заголовок',
                text='Текст.',
                slug=f'{index}',
                author=cls.user
            )
            for index in range(2)
        )

    def test_notes_order(self):
        self.client.force_login(self.user)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        all_id = [note.id for note in object_list]
        sorted_id = sorted(all_id)
        self.assertEqual(all_id, sorted_id)

import pytest
from django.test.client import Client
from notes.models import Note


@pytest.fixture
def author(django_user_model):
    """Фикстура для создания автора."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Фикстура для создания другого пользователя."""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    """Фикстура для создания клиента автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Фикстура для создания клиента другого пользователя."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def note(author):
    """Фикстура для создания заметки."""
    note = Note.objects.create(
        title='Заголовок',
        text='Текст заметки',
        slug='note-slug',
        author=author
    )
    return note


@pytest.fixture
def slug_for_args(note):
    """Фикстура для возврата поля slug."""
    return (note.slug,)

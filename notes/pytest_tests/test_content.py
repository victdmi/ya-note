import pytest
from pytest_lazy_fixtures import lf

from django.urls import reverse

from notes.forms import NoteForm


@pytest.mark.parametrize(
    'parametrized_client, note_in_list',
    (
        (lf('author_client'), True),
        (lf('not_author_client'), False)
    )
)
def test_notes_list_for_different_users(
    note, parametrized_client, note_in_list
):
    """Тест отображения заметок для разных пользователей."""
    url = reverse('notes:list')
    response = parametrized_client.get(url)
    object_list = response.context['object_list']
    assert (note in object_list) is note_in_list


@pytest.mark.parametrize(
    'name, args',
    (
        ('notes:add', None),
        ('notes:edit', lf('slug_for_args'))
    )
)
def test_pages_contain_form(author_client, name, args):
    """Тест присутствия формы на странице."""
    url = reverse(name, args=args)
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], NoteForm)

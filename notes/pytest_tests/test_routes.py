from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazy_fixtures import lf

from django.urls import reverse


@pytest.mark.parametrize(
    'name',
    ('notes:home', 'users:login', 'users:logout', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name):
    """Тест доступности страниц для неавторизованного пользователя."""
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
        'parametrized_client, expected_status',
        (
            (lf('not_author_client'), HTTPStatus.NOT_FOUND),
            (lf('author_client'), HTTPStatus.OK)
        ),
)
@pytest.mark.parametrize(
        'name',
        ('notes:detail', 'notes:edit', 'notes:delete')
)
def test_pages_availability_for_different_users(
    parametrized_client, expected_status, name, note
):
    """Тест доступности страниц для разных пользователей."""
    url = reverse(name, args=(note.slug,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('notes:detail', lf('slug_for_args')),
        ('notes:edit', lf('slug_for_args')),
        ('notes:delete', lf('slug_for_args')),
        ('notes:add', None),
        ('notes:success', None),
        ('notes:list', None)
    )
)
def test_redirects(client, name, args):
    """Тест редиректов для неавторизованных пользователей."""
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)

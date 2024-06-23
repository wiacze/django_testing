from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestBase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.auth_user = User.objects.create(
            username='Авторизованный пользователь'
        )
        cls.author_client = Client()
        cls.auth_user_client = Client()
        cls.author_client.force_login(cls.author)
        cls.auth_user_client.force_login(cls.auth_user)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
        )
        cls.note_form = {
            'title': 'Заголовок №2',
            'text': 'Текст №2',
            'slug': 'second-slug'
        }
        cls.edit_form = {
            'title': 'Измененный заголовок',
            'text': 'Измененный текст',
            'slug': 'edit-slug'
        }
        cls.DEFAULT_NOTES_COUNT = Note.objects.count()
        cls.EDIT_URL = reverse('notes:edit', args=(cls.note.slug,))
        cls.DELETE_URL = reverse('notes:delete', args=(cls.note.slug,))
        cls.DETAIL_URL = reverse('notes:detail', args=(cls.note.slug,))
        cls.HOME_URL = reverse('notes:home')
        cls.LOGIN_URL = reverse('users:login')
        cls.LOGOUT_URL = reverse('users:logout')
        cls.SIGNUP_URL = reverse('users:signup')
        cls.LIST_URL = reverse('notes:list')
        cls.ADD_URL = reverse('notes:add')
        cls.SUCCESS_URL = reverse('notes:success')

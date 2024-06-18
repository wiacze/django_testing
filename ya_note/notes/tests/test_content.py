from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestContent(TestCase):
    NOTES_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.first_user = User.objects.create(username='Первый пользователь')
        cls.second_user = User.objects.create(username='Второй пользователь')
        cls.first_client = Client()
        cls.second_client = Client()
        cls.first_client.force_login(cls.first_user)
        cls.second_client.force_login(cls.second_user)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.first_user,
        )

    def test_notes_for_diff_users(self):
        users_statuses = (
            (self.first_client, True),
            (self.second_client, False),
        )
        for user, status in users_statuses:
            with self.subTest():
                response = user.get(self.NOTES_URL)
                object_list = response.context['object_list']
                self.assertEqual(self.note in object_list, status)

    def test_form_in_pages(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.first_client.get(url)
                self.assertIn('form', response.context)

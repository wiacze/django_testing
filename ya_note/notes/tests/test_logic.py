from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING


User = get_user_model()


class TestLogic(TestCase):

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
            slug='slug',
            author=cls.first_user,
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
        cls.ADD_URL = reverse('notes:add')
        cls.SUCCESS_URL = reverse('notes:success')
        cls.LOGIN_URL = reverse('users:login')
        cls.EDIT_URL = reverse('notes:edit', args=(cls.note.slug,))
        cls.DELETE_URL = reverse('notes:delete', args=(cls.note.slug,))

    def test_creation_by_auth_user(self):
        response = self.first_client.post(
            self.ADD_URL,
            data=self.note_form
        )
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), self.DEFAULT_NOTES_COUNT + 1)
        new_note = Note.objects.order_by('id').last()
        self.assertEqual(new_note.title, self.note_form['title'])
        self.assertEqual(new_note.text, self.note_form['text'])
        self.assertEqual(new_note.slug, self.note_form['slug'])
        self.assertEqual(new_note.author, self.first_user)

    def test_creation_by_anon_user(self):
        response = self.client.post(self.ADD_URL, data=self.note_form)
        expected_url = f'{self.LOGIN_URL}?next={self.ADD_URL}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), self.DEFAULT_NOTES_COUNT)

    def test_editing_by_author(self):
        response = self.first_client.post(
            self.EDIT_URL,
            data=self.edit_form
        )
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), self.DEFAULT_NOTES_COUNT)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.edit_form['title'])
        self.assertEqual(new_note.text, self.edit_form['text'])
        self.assertEqual(new_note.slug, self.edit_form['slug'])

    def test_editing_by_other_user(self):
        response = self.second_client.post(
            self.EDIT_URL,
            data=self.edit_form
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        original_note = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, original_note.title)
        self.assertEqual(self.note.text, original_note.text)
        self.assertEqual(self.note.text, original_note.text)

    def test_deletion_by_author(self):
        response = self.first_client.post(self.DELETE_URL)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), self.DEFAULT_NOTES_COUNT - 1)

    def test_deletion_by_other_user(self):
        response = self.second_client.post(self.DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), self.DEFAULT_NOTES_COUNT)

    def test_slug(self):
        self.note_form['slug'] = self.note.slug
        response = self.first_client.post(
            self.ADD_URL,
            data=self.note_form
        )
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), self.DEFAULT_NOTES_COUNT)

    def test_slugify(self):
        self.note_form.pop('slug')
        response = self.first_client.post(
            self.ADD_URL,
            data=self.note_form
        )
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), self.DEFAULT_NOTES_COUNT + 1)
        new_note = Note.objects.order_by('id').last()
        expected_slug = slugify(self.note_form['title'])
        self.assertEqual(new_note.slug, expected_slug)

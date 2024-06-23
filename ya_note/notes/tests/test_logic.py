from http import HTTPStatus

from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING
from .base import TestBase


class TestLogic(TestBase):

    def count_examination(self, create=False, delete=False):
        count = self.DEFAULT_NOTES_COUNT
        if create:
            count += 1
        if delete:
            count -= 1
        self.assertEqual(Note.objects.count(), count)

    def identity_verification(self, new_note, form):
        self.assertEqual(new_note.title, form['title'])
        self.assertEqual(new_note.text, form['text'])
        self.assertEqual(new_note.slug, form['slug'])

    def redirect_examination(
        self, client, url, form, redirect_url, redirect=True
    ):
        response = client.post(
            url, data=form
        )
        if redirect:
            self.assertRedirects(response, redirect_url)
        else:
            self.assertEqual(response.status_code, redirect_url)

    def test_creation_by_auth_user(self):
        self.redirect_examination(
            self.author_client,
            self.ADD_URL,
            self.note_form,
            self.SUCCESS_URL
        )
        new_note = Note.objects.order_by('id').last()
        self.identity_verification(new_note, self.note_form)
        self.count_examination(create=True)
        self.assertEqual(new_note.author, self.author)

    def test_creation_by_anon_user(self):
        expected_url = f'{self.LOGIN_URL}?next={self.ADD_URL}'
        self.redirect_examination(
            self.client,
            self.ADD_URL,
            self.note_form,
            expected_url)
        self.count_examination()

    def test_editing_by_author(self):
        self.redirect_examination(
            self.author_client,
            self.EDIT_URL,
            self.edit_form,
            self.SUCCESS_URL
        )
        self.count_examination()
        new_note = Note.objects.get()
        self.identity_verification(new_note, self.edit_form)

    def test_editing_by_other_user(self):
        self.redirect_examination(
            self.auth_user_client,
            self.EDIT_URL,
            self.edit_form,
            HTTPStatus.NOT_FOUND,
            redirect=False
        )
        original_note = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, original_note.title)
        self.assertEqual(self.note.text, original_note.text)
        self.assertEqual(self.note.text, original_note.text)

    def test_deletion_by_author(self):
        response = self.author_client.post(self.DELETE_URL)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.count_examination(delete=True)

    def test_deletion_by_other_user(self):
        response = self.auth_user_client.post(self.DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.count_examination()

    def test_slug(self):
        self.note_form['slug'] = self.note.slug
        response = self.author_client.post(
            self.ADD_URL,
            data=self.note_form
        )
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING)
        )
        self.count_examination()

    def test_slugify(self):
        self.note_form.pop('slug')
        self.redirect_examination(
            self.author_client,
            self.ADD_URL,
            self.note_form,
            self.SUCCESS_URL
        )
        self.count_examination(create=True)
        new_note = Note.objects.order_by('id').last()
        expected_slug = slugify(self.note_form['title'])
        self.assertEqual(new_note.slug, expected_slug)

from . import base


class TestContent(base.TestBase):

    def test_notes_for_diff_users(self):
        users_statuses = (
            (self.author_client, True),
            (self.auth_user_client, False),
        )
        for user, status in users_statuses:
            with self.subTest():
                response = user.get(self.LIST_URL)
                object_list = response.context['object_list']
                self.assertEqual(self.note in object_list, status)

    def test_form_in_pages(self):
        urls = (
            self.ADD_URL,
            self.EDIT_URL,
        )
        for url in urls:
            with self.subTest(name=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)

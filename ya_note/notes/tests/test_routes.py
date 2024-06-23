from http import HTTPStatus

from .base import TestBase


class TestRoutes(TestBase):

    def examination(self, users_statuses, urls, logged=False, redirect=False):
        for user, status in users_statuses:
            if logged:
                self.client.force_login(user)
            for url in urls:
                with self.subTest(user=user, name=url):
                    redirect_url = f'{self.LOGIN_URL}?next={url}'
                    response = self.client.get(url)
                    if redirect:
                        self.assertRedirects(response, redirect_url)
                    else:
                        self.assertEqual(response.status_code, status)

    def test_pages_availability(self):
        users_statuses = (
            (None, HTTPStatus.OK),
        )
        urls = (
            self.HOME_URL,
            self.LOGIN_URL,
            self.LOGOUT_URL,
            self.SIGNUP_URL,
        )
        self.examination(users_statuses, urls)

    def test_page_available_for_auth_user(self):
        users_statuses = (
            (self.auth_user, HTTPStatus.OK),
        )
        urls = (
            self.LIST_URL,
            self.ADD_URL,
            self.SUCCESS_URL,
        )
        self.examination(users_statuses, urls, logged=True)

    def test_availability_for_comment_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.auth_user, HTTPStatus.NOT_FOUND),
        )
        urls = (
            self.EDIT_URL,
            self.DELETE_URL,
            self.DETAIL_URL,
        )
        self.examination(users_statuses, urls, logged=True)

    def test_redirect_for_anonymous_client(self):
        users_statuses = (
            (None, None),
        )
        urls = (
            self.LIST_URL,
            self.ADD_URL,
            self.SUCCESS_URL,
            self.EDIT_URL,
            self.DELETE_URL,
            self.DETAIL_URL,
        )
        self.examination(users_statuses, urls, redirect=True)

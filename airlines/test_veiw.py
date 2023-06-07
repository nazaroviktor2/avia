from django.urls import reverse
from django_filters.compat import TestCase

from string import ascii_lowercase as letters
from rest_framework.status import HTTP_200_OK as OK
from django.contrib.auth.models import User


def create_view_tests(url, page_name, template):
    class ViewTests(TestCase):
        def setUp(self):
            default = letters[:10]
            self.user = User.objects.create_user(username=default, password=default)
            self.client.login(username=default, password=default)

        def test_view_exists_at_url(self):
            self.assertEqual(self.client.get(url).status_code, OK)

        def test_view_exists_by_name(self):
            self.assertEqual(
                self.client.get(
                reverse(page_name)
                ).status_code, OK
            )

        def test_view_uses_template(self):
            resp = self.client.get(reverse(page_name))
            self.assertEqual(resp.status_code, OK)
            self.assertTemplateUsed(resp, template)

    return ViewTests


LoginViewTest = create_view_tests(
    '/login/',
    'login',
    'login.html'
)
RegisterViewTest = create_view_tests(
    '/register/',
    'register',
    'register.html'
)

ProfileViewTest = create_view_tests(
    '/find/',
    'find_flight',
    'find_flight.html'
)

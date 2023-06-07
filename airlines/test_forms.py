from airlines import forms

from django_filters.compat import TestCase


class TransferFromTest(TestCase):

    def test_form_valid(self):
        request_data = {
            'first_name': "test",
            'last_name': "test",
            'username': "test",
            "password": "confirmconfirm123",
            "confirm": "confirmconfirm123"
        }
        form = forms.ClientRegistrationForm(request_data)
        self.assertTrue(form.is_valid())

    def test_form_notvalid(self):
        request_data = {
            'first_name': "test",
            'last_name': "test",
            'username': "test",
            "password": "confirmconfirm123",
            "confirm": "confirmconfirm123222"
        }
        form = forms.ClientRegistrationForm(request_data)
        self.assertFalse(form.is_valid())

import json

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token


# Create your tests here.

def create_viewset_tests(url, request_content):
    class ViewSetTests(TestCase):

        def setUp(self):
            self.creds_user = {'username': 'user', 'password': 'user'}
            self.creds_superuser = {'username': 'superuser', 'password': 'superuser'}
            self.user = User.objects.create_user(**self.creds_user)
            self.superuser = User.objects.create_user(is_superuser=True, **self.creds_superuser)
            self.token = Token.objects.create(user=self.superuser)
            self.client.login(**self.creds_superuser)

        def test_get(self):
            # logging in with user
            self.client.logout()
            self.client.login(**self.creds_user)
            resp_get = self.client.get(url)
            self.assertEqual(resp_get.status_code, status.HTTP_200_OK)

        def test_post(self):
            resp_post = self.client.post(url, request_content)
            self.assertEqual(resp_post.status_code, status.HTTP_201_CREATED)

        def test_put(self):
            resp_post = self.client.post(url, request_content)
            id = json.loads(resp_post.content.decode('utf8'))["id"]
            self.assertEqual(resp_post.status_code, status.HTTP_201_CREATED)
            resp_post = self.client.put(url + f'{id}', request_content, follow=True)
            self.assertEqual(resp_post.status_code, status.HTTP_200_OK)

        def test_delete(self):
            resp_post = self.client.post(url, request_content)
            id = json.loads(resp_post.content.decode('utf8'))["id"]
            self.assertEqual(resp_post.status_code, status.HTTP_201_CREATED)
            resp_del = self.client.delete(url + f'{id}/', follow=True)
            self.assertEqual(resp_del.status_code, status.HTTP_204_NO_CONTENT)
            rest_get = self.client.get(url + f'{id}/', follow=True)
            self.assertEqual(rest_get.status_code, status.HTTP_404_NOT_FOUND)

    return ViewSetTests


countryTest = create_viewset_tests("/api/v1/country/", {"name": "TestCountry"})
ModelAirplane = create_viewset_tests("/api/v1/model-airplane/",
                                     {"name": "test", "seats": 1,
                                      "load_capacity": 100,
                                      "scheme": json.dumps({
                                          "model_name": 1,
                                          "rows": 1,
                                          "columns": 1,
                                          "seats": [{
                                              "id": 1,
                                              "row": 1,
                                              "column": 1,
                                              "available": True,
                                              "name": "A1"
                                          }]
                                      })
                                      })
# CityTest = create_viewset_tests("/api/v1/city/", {"name":"City", "country":{
#     'name':"dsad"
# }})

import sys

from django.test import TestCase
from django.urls import reverse

sys.path.append('../seenit')

from seenit.models import User


class ViewsTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user("test", "test@test.com", "secret")
        user.save()


class HomeViewTests(ViewsTestCase):
    def test_logged_out(self):
        response = self.client.get(reverse("seenit:home"))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse("seenit:home"), follow=True)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_logged_in(self):
        self.client.login(username="test", password="secret")
        response = self.client.get(reverse("seenit:home"))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse("seenit:home"), follow=True)
        self.assertTemplateUsed(response, 'seenit/user_detail.html')


class RegisterViewTests(TestCase):
    def test_call_view_get_request(self):
        response = self.client.get(reverse('seenit:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'seenit/auth/register.html')

    def test_call_view_post_request_success(self):
        response = self.client.post(reverse('seenit:register'), data={
                                    'username': 'test',
                                    'email': 'test@test.com',
                                    'password1': 'j45dk29dk',
                                    'password2': 'j45dk29dk'}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'seenit/user_detail.html')
        self.assertContains(response, "Hello, test")

    def test_call_view_post_request_fail(self):
        response = self.client.post(reverse('seenit:register'), data={
                                    'username': 'test',
                                    'email': 'test@test.com',
                                    'password1': 'badpw',
                                    'password2': 'badpw'}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'seenit/auth/register.html')
        self.assertContains(response, "This password is too short")

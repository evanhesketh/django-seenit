from seenit.models import User, Channel
from seenit.forms import ChannelForm, PostForm

from django.test import TestCase
from django.urls import reverse


class ViewsTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user("test", "test@test.com", "secret")
        user.save()

        self.user_id = user.id

        channel = Channel(name="test channel")
        channel.save()

        self.channel_id = channel.id


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


class UserDetailViewTests(ViewsTestCase):
    def test_logged_out(self):
        response = self.client.get(
            reverse("seenit:user_detail", kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(
            reverse("seenit:user_detail", kwargs={'pk': 1}), follow=True)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_logged_in(self):
        self.client.login(username="test", password="secret")
        response = self.client.get(
            reverse("seenit:user_detail", kwargs={'pk': self.user_id}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'seenit/user_detail.html')
        self.assertContains(response, "Hello, test")

    def test_logged_in_context_data(self):
        self.client.login(username="test", password="secret")
        response = self.client.get(
            reverse("seenit:user_detail", kwargs={'pk': self.user_id}))

        user = User.objects.get(id=self.user_id)

        self.assertEqual(response.context['channel_highlights'], [])
        self.assertQuerySetEqual(response.context['top_posts'], [])
        self.assertEqual(response.context['object'], user)


class ChannelCreateViewTests(ViewsTestCase):
    def test_call_view_logged_out(self):
        response = self.client.post(
            reverse("seenit:create_channel"))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse("seenit:home"), follow=True)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_call_view_post_request_logged_in(self):
        self.client.login(username="test", password="secret")
        response = self.client.post(reverse("seenit:create_channel"), data={
                                    "name": "new test channel"}, follow=True)

        self.assertContains(response, "new test channel")

    def test_call_view_get_request_logged_in(self):
        self.client.login(username="test", password="secret")
        response = self.client.get(reverse("seenit:create_channel"))
        self.assertEqual(response.status_code, 403)


class ChannelListViewTests(ViewsTestCase):
    def test_call_view_logged_out(self):
        response = self.client.get(
            reverse("seenit:channels"))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse("seenit:home"), follow=True)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_call_view_logged_in(self):
        self.client.login(username="test", password="secret")
        response = self.client.get(
            reverse("seenit:channels"), follow=True)
        self.assertContains(response, "test channel")
        self.assertTemplateUsed(response, "seenit/channel_list.html")

    def test_logged_in_context_data(self):
        self.client.login(username="test", password="secret")
        response = self.client.get(
            reverse("seenit:channels"), follow=True)
        channels = Channel.objects.all()

        self.assertIsInstance(response.context['form'], ChannelForm)
        self.assertQuerySetEqual(response.context['channel_list'], channels)


class ChannelDetailViewTests(ViewsTestCase):
    def test_call_view_logged_out(self):
        response = self.client.get(
            reverse("seenit:channel_detail", kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(
            reverse("seenit:channel_detail", kwargs={'pk': 1}), follow=True)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_call_view_logged_in_success(self):
        self.client.login(username="test", password="secret")
        response = self.client.get(
            reverse("seenit:channel_detail", kwargs={'pk': self.channel_id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test channel")
        self.assertTemplateUsed(response, 'seenit/channel_detail.html')

    def test_logged_in_context_data(self):
        self.client.login(username="test", password="secret")
        response = self.client.get(
            reverse("seenit:channel_detail", kwargs={'pk': self.channel_id}))

        self.assertEqual(response.context['channel_id'], self.channel_id)
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertEqual(response.context['user_subscribed'], False)


class ChannelDetailFormViewTests(ViewsTestCase):
    def test_call_view_logged_out(self):
        response = self.client.get(
            reverse("seenit:channel_detail", kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(
            reverse("seenit:channel_detail", kwargs={'pk': 1}), follow=True)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_call_view_logged_in_success(self):
        self.client.login(username="test", password="secret")
        response = self.client.post(
            reverse("seenit:channel_detail", kwargs={"pk": self.channel_id}),
            data={"title": "new post title", "text": "new post text"},
            follow=True)

        self.assertTemplateUsed(response, 'seenit/channel_detail.html')
        self.assertContains(response, "new post title")

import sys
sys.path.append('../seenit')

from django.test import TestCase

from seenit.models import User, Post, Channel


class ModelsTestCase(TestCase):
    def setUp(self):
        u1 = User(username="test", email="test@test.com", password="secret")
        u2 = User(username="test2", email="test2@test.com", password="secret")
        u1.save()
        u2.save()

        self.u1_id = u1.id
        self.u2_id = u2.id

        c1 = Channel(name="channel1")
        c2 = Channel(name="channel2")
        c1.save()
        c2.save()

        self.c1_id = c1.id
        self.c2_id = c2.id

        p1 = Post(title="post1", text="abcabc", user=u1, channel=c1)
        p2 = Post(title="post2", text="abcabc", user=u1, channel=c1)
        p1.save()
        p2.save()

        self.p1_id = p1.id
        self.p2_id = p2.id

    def tearDown(self):
        User.objects.all().delete()
        Channel.objects.all().delete()
        Post.objects.all().delete()


class UserModelTests(ModelsTestCase):
    def test_user_model(self):
        user = User.objects.filter(id=self.u1_id)
        self.assertEqual(len(user), 1)

    def test_user_top_posts(self):
        user = User.objects.filter(id=self.u1_id)
        post = Post.objects.filter(id=self.p1_id)
        channel = Channel.objects.filter(id=self.c1_id)

        posts = user[0].get_top_posts()

        self.assertEqual(len(posts), 2)
        self.assertIn(post[0], posts)

        p3 = Post(title="post3", text="abcabc", user=user[0],
                  channel=channel[0])
        p3.save()

        posts = user[0].get_top_posts()
        self.assertEqual(len(posts), 3)
        self.assertIn(p3, posts)

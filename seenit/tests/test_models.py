import sys
from django.test import TestCase

sys.path.append('../seenit')

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
        user = User.objects.get(id=self.u1_id)
        post = Post.objects.get(id=self.p1_id)
        channel = Channel.objects.get(id=self.c1_id)

        posts = user.get_top_posts()

        self.assertEqual(len(posts), 2)
        self.assertIn(post, posts)

        p3 = Post(title="post3", text="abcabc", user=user,
                  channel=channel)
        p3.save()

        posts = user.get_top_posts()
        self.assertEqual(len(posts), 3)
        self.assertIn(p3, posts)


class ChannelModelTests(ModelsTestCase):
    def test_channel_model(self):
        channel = Channel.objects.filter(id=self.c1_id)
        self.assertEqual(len(channel), 1)

    def test_determine_if_user_subscribed(self):
        channel = Channel.objects.get(id=self.c1_id)
        user = User.objects.get(id=self.u1_id)

        self.assertFalse(channel.determine_if_user_subscribed(user))

        channel.subscribed_users.add(user)

        self.assertTrue(channel.determine_if_user_subscribed(user))


class PostModelTests(ModelsTestCase):
    def test_post_model(self):
        post = Post.objects.filter(id=self.p1_id)
        self.assertEqual(len(post), 1)

    def test_post_upvote_neutral(self):
        post = Post.objects.get(id=self.p1_id)

        self.assertEqual(post.rating, 0)
        self.assertFalse(post.up_votes.exists())

        user = User.objects.get(id=self.u1_id)
        post.upvote(user)

        user_who_up_voted = post.up_votes.get(id=self.u1_id)

        self.assertEqual(post.rating, 1)
        self.assertEqual(user, user_who_up_voted)

    def test_post_upvote_from_downvote(self):
        post = Post.objects.get(id=self.p1_id)
        user = User.objects.get(id=self.u1_id)
        post.down_votes.add(user)
        post.rating = -1

        self.assertEqual(post.rating, -1)
        self.assertTrue(post.down_votes.exists())
        self.assertFalse(post.up_votes.exists())

        post.upvote(user)

        self.assertEqual(post.rating, 0)
        self.assertFalse(post.down_votes.exists())
        self.assertFalse(post.up_votes.exists())

    def test_post_downvote_netural(self):
        post = Post.objects.get(id=self.p1_id)

        self.assertEqual(post.rating, 0)
        self.assertFalse(post.down_votes.exists())

        user = User.objects.get(id=self.u1_id)
        post.downvote(user)

        user_who_down_voted = post.down_votes.get(id=self.u1_id)

        self.assertEqual(post.rating, -1)
        self.assertEqual(user, user_who_down_voted)

    def test_post_downvote_from_upvote(self):
        post = Post.objects.get(id=self.p1_id)
        user = User.objects.get(id=self.u1_id)
        post.up_votes.add(user)
        post.rating = 1

        self.assertEqual(post.rating, 1)
        self.assertFalse(post.down_votes.exists())
        self.assertTrue(post.up_votes.exists())

        post.downvote(user)

        self.assertEqual(post.rating, 0)
        self.assertFalse(post.down_votes.exists())
        self.assertFalse(post.up_votes.exists())

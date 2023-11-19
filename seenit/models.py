from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from mptt.models import MPTTModel, TreeForeignKey


class User(AbstractUser):
    """Model for a user."""

    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=400, db_column='hashed_password')
    # related names:

    # posts
    # subscribed_channels
    # comment_up_votes
    # comment_down_votes
    # post_up_votes
    # post_down_votes


class Channel(models.Model):
    """Model for a channel."""

    name = models.CharField(max_length=50, unique=True)
    subscribed_users = models.ManyToManyField(
        User, related_name="subscribed_channels", blank=True)

    def determine_if_user_subscribed(self, user):
        if user in self.subscribed_users.filter(id=user.id):
            return True
        return False


class Post(models.Model):
    """Model for a post."""

    class Meta:
        ordering = ['-rating', '-pub_date']

    title = models.CharField(max_length=255)
    text = models.TextField()
    rating = models.IntegerField(default=0)
    up_votes = models.ManyToManyField(
        User, related_name="post_up_votes", blank=True)
    down_votes = models.ManyToManyField(
        User, related_name="post_down_votes", blank=True)
    pub_date = models.DateTimeField(default=timezone.now)
    channel = models.ForeignKey(
        Channel, related_name="posts", on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, related_name="posts", on_delete=models.CASCADE)


class Comment(MPTTModel):
    """model for a comment on a post."""

    text = models.TextField()
    rating = models.IntegerField(default=0)
    up_votes = models.ManyToManyField(
        User, related_name="comment_up_votes", blank=True)
    down_votes = models.ManyToManyField(
        User, related_name="comment_down_votes", blank=True)
    pub_date = models.DateTimeField(default=timezone.now)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True,
                            blank=True, related_name='children')
    post = models.ForeignKey(
        Post, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, related_name="comments", on_delete=models.CASCADE)

    class MPTTMeta:
        order_insertion_by = ['-rating', '-pub_date']

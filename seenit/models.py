from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from mptt.models import MPTTModel, TreeForeignKey


class User(AbstractUser):
    """Model for a user."""

    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=400, db_column='hashed_password')
    # posts -> refers to Posts
    # subscribed_channels -> refers to Channel


class Channel(models.Model):
    """Model for a channel."""

    name = models.CharField(max_length=50, unique=True)
    subscribed_users = models.ManyToManyField(
        User, related_name="subscribed_channels", blank=True)


class Post(models.Model):
    """Model for a post."""

    class Meta:
        ordering = ['-rating', '-pub_date']

    title = models.CharField(max_length=255)
    text = models.TextField()
    rating = models.IntegerField(default=0)
    pub_date = models.DateTimeField(default=timezone.now)
    channel = models.ForeignKey(
        Channel, related_name="posts", on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, related_name="posts", on_delete=models.CASCADE)


class Comment(MPTTModel):
    """model for a comment on a post."""

    text = models.TextField()
    rating = models.IntegerField(default=0)
    pub_date = models.DateTimeField(default=timezone.now)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True,
                            blank=True, related_name='children')
    post = models.ForeignKey(
        Post, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, related_name="comments", on_delete=models.CASCADE)

    class MPTTMeta:
        order_insertion_by = ['-rating', '-pub_date']

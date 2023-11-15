from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Model for a user."""

    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(db_column='hashed_password')
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

    title = models.CharField(max_length=100)
    text = models.CharField()
    rating = models.IntegerField(default=0)
    pub_date = models.DateTimeField(default=timezone.now)
    channel = models.ForeignKey(
        Channel, related_name="posts", on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, related_name="posts", on_delete=models.CASCADE)


class Comment(models.Model):
    """model for a comment on a post."""

    class Meta:
        ordering = ['-rating', '-pub_date']

    text = models.CharField()
    rating = models.IntegerField(default=0)
    pub_date = models.DateTimeField(default=timezone.now)
    is_reply = models.BooleanField(default=False)
    post = models.ForeignKey(
        Post, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, related_name="comments", on_delete=models.CASCADE)
    replies = models.ManyToManyField("self", symmetrical=False, blank=True)

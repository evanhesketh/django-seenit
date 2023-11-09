from django.contrib.auth.models import AbstractUser
from django.db import models


class Channel(models.Model):
    """Model for a channel."""

    name = models.CharField(max_length=50, unique=True)


class User(AbstractUser):
    """Model for a user."""

    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(db_column='hashed_password')
    subscribed_channels = models.ManyToManyField(Channel, blank=True)
    # posts -> user's posts


class Post(models.Model):
    """Model for a post."""

    title = models.CharField(max_length=100)
    text = models.CharField()
    rating = models.IntegerField(default=0)
    channel_id = models.ForeignKey(Channel, on_delete=models.CASCADE)
    user_id = models.ForeignKey(
        User, related_name="posts", on_delete=models.CASCADE)


class Comment(models.Model):
    """model for a comment on a post."""

    text = models.CharField()
    rating = models.IntegerField(default=0)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    replies = models.ManyToManyField("self", symmetrical=False, blank=True)

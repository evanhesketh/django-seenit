from django.db import models


class User(models.Model):
    """ Model for a user."""

    username = models.CharField(max_length=50)
    email = models.EmailField()
    hashed_password = models.CharField(max_length=50)

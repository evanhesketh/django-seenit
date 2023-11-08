from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """ Model for a user."""

    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(db_column='hashed_password')

    

#     @classmethod
#     def signup(cls, username, email, password):
#         """
#         Sign up a user.

#         Hashes password and adds user to db.
#         """

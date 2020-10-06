from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    numberOfVotes = models.IntegerField(default=5)

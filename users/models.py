from django.contrib.auth.models import AbstractUser
from django.db import models


class UserAccount(AbstractUser):
    USER_ROLES = [
        ('C', 'Company'),
        ('W', 'Worker'),
        ('A', 'Admin'),
    ]
    last_login = None
    first_name = None
    last_name = None
    role = models.CharField(
        max_length=1,
        choices=USER_ROLES,
    )

    def __str__(self):
        return self.username

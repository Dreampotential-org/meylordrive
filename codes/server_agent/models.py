# models.py in your app (e.g., server_agent)
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Add your custom fields if needed
    api_key = models.CharField(max_length=255, unique=True)

    # Fix clashes in reverse accessors
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_set",
        related_query_name="custom_user",
        blank=True,
        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_set",
        related_query_name="custom_user",
        blank=True,
        help_text="Specific permissions for this user.",
    )

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model for the travel API."""

    class RoleChoices(models.TextChoices):
        TRAVELER = "traveler", "Traveler"
        ADMIN = "admin", "Admin"

    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.TRAVELER,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["username"]
        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return self.username
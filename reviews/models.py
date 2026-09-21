from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from bookings.models import Accommodation, Activity
from destinations.models import Destination


class Review(models.Model):
    """User reviews for destinations, accommodations or activities."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name="reviews",
        null=True,
        blank=True,
    )

    accommodation = models.ForeignKey(
        Accommodation,
        on_delete=models.CASCADE,
        related_name="reviews",
        null=True,
        blank=True,
    )

    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name="reviews",
        null=True,
        blank=True,
    )

    rating = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ]
    )

    title = models.CharField(
        max_length=200,
    )

    content = models.TextField()

    visit_date = models.DateField()

    images = models.TextField(
        blank=True,
        default="",
    )

    helpful_count = models.PositiveIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["destination", "rating"]
            ),
            models.Index(
                fields=["user"]
            ),
        ]

    def __str__(self):
        return f"{self.title} by {self.user.username}"

    def clean(self):
        """Ensure a review targets exactly one item."""

        review_targets = [
            self.destination,
            self.accommodation,
            self.activity,
        ]

        if sum(
            1 for target in review_targets if target
        ) != 1:
            raise ValidationError(
                "Review must be for exactly one item"
            )
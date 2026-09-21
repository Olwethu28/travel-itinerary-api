from django.core.validators import MinValueValidator
from django.db import models


class Destination(models.Model):
    """A travel destination that users can visit."""

    class CategoryChoices(models.TextChoices):
        BEACH = "beach", "Beach"
        MOUNTAIN = "mountain", "Mountain"
        CITY = "city", "City"
        CULTURAL = "cultural", "Cultural"
        ADVENTURE = "adventure", "Adventure"
        RELAXATION = "relaxation", "Relaxation"

    class ClimateChoices(models.TextChoices):
        TROPICAL = "tropical", "Tropical"
        DRY = "dry", "Dry"
        TEMPERATE = "temperate", "Temperate"
        COLD = "cold", "Cold"
        MEDITERRANEAN = "mediterranean", "Mediterranean"

    name = models.CharField(
        max_length=200,
        unique=True,
    )

    country = models.CharField(
        max_length=100,
    )

    description = models.TextField()

    category = models.CharField(
        max_length=20,
        choices=CategoryChoices.choices,
    )

    climate = models.CharField(
        max_length=20,
        choices=ClimateChoices.choices,
    )

    best_time_to_visit = models.CharField(
        max_length=200,
    )

    avg_daily_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    image = models.ImageField(
        upload_to="destinations/",
        null=True,
        blank=True,
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["name"]

        indexes = [
            models.Index(
                fields=["country", "category"]
            ),
            models.Index(
                fields=["climate"]
            ),
        ]

    def __str__(self):
        return f"{self.name}, {self.country}"

    @property
    def average_rating(self):
        """Calculate the average rating from reviews."""
        ratings = self.reviews.aggregate(
            models.Avg("rating")
        )

        return ratings["rating__avg"] or 0
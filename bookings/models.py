from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from destinations.models import Destination
from itineraries.models import Itinerary


class Accommodation(models.Model):
    """Hotels, hostels and vacation rentals."""

    class TypeChoices(models.TextChoices):
        HOTEL = "hotel", "Hotel"
        HOSTEL = "hostel", "Hostel"
        RENTAL = "rental", "Vacation Rental"
        RESORT = "resort", "Resort"
        BNB = "bnb", "B&B"

    name = models.CharField(
        max_length=200,
    )

    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name="accommodations",
    )

    accommodation_type = models.CharField(
        max_length=10,
        choices=TypeChoices.choices,
    )

    description = models.TextField()

    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    max_guests = models.PositiveIntegerField()

    amenities = models.TextField(
        blank=True,
        default="",
    )

    address = models.CharField(
        max_length=300,
    )

    contact_email = models.EmailField()

    contact_phone = models.CharField(
        max_length=20,
    )

    image = models.ImageField(
        upload_to="accommodations/",
        null=True,
        blank=True,
    )

    is_available = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["name"]

        indexes = [
            models.Index(
                fields=[
                    "destination",
                    "accommodation_type",
                ]
            ),
        ]

    def __str__(self):
        return (
            f"{self.name} "
            f"({self.get_accommodation_type_display()})"
        )


class Activity(models.Model):
    """Tours, attractions and experiences."""

    class CategoryChoices(models.TextChoices):
        TOUR = "tour", "Tour"
        ATTRACTION = "attraction", "Attraction"
        DINING = "dining", "Dining"
        SHOPPING = "shopping", "Shopping"
        ENTERTAINMENT = "entertainment", "Entertainment"
        OUTDOOR = "outdoor", "Outdoor"

    name = models.CharField(
        max_length=200,
    )

    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name="activities",
    )

    category = models.CharField(
        max_length=20,
        choices=CategoryChoices.choices,
    )

    description = models.TextField()

    duration_hours = models.DecimalField(
        max_digits=4,
        decimal_places=1,
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    max_participants = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    requirements = models.TextField(
        blank=True,
    )

    image = models.ImageField(
        upload_to="activities/",
        null=True,
        blank=True,
    )

    is_available = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["name"]

        verbose_name_plural = "Activities"

        indexes = [
            models.Index(
                fields=["destination", "category"]
            ),
        ]

    def __str__(self):
        return f"{self.name} - {self.destination.name}"


class Booking(models.Model):
    """User bookings for accommodations or activities."""

    class StatusChoices(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
    )

    itinerary = models.ForeignKey(
        Itinerary,
        on_delete=models.CASCADE,
        related_name="bookings",
    )

    accommodation = models.ForeignKey(
        Accommodation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bookings",
    )

    activity = models.ForeignKey(
        Activity,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bookings",
    )

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )

    booking_date = models.DateField()

    quantity = models.PositiveIntegerField(
        default=1,
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
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
                fields=["user", "status"]
            ),
            models.Index(
                fields=["itinerary"]
            ),
        ]

    def __str__(self):
        if self.accommodation:
            return f"Booking: {self.accommodation.name}"

        if self.activity:
            return f"Booking: {self.activity.name}"

        return f"Booking #{self.id}"

    def clean(self):
        """Ensure a booking targets exactly one item."""

        if not self.accommodation and not self.activity:
            raise ValidationError(
                "Booking must have either accommodation or activity"
            )

        if self.accommodation and self.activity:
            raise ValidationError(
                "Booking cannot have both accommodation and activity"
            )
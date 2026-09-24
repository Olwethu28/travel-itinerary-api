from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase

from destinations.models import Destination
from itineraries.models import Itinerary

from .models import Accommodation, Activity, Booking
from .serializers import (
    AccommodationSerializer,
    ActivitySerializer,
    BookingCreateSerializer,
    BookingSerializer,
)


User = get_user_model()


class BookingSerializerTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="olwethu",
            email="olwethu@example.com",
            password="Password123!",
        )

        self.destination = Destination.objects.create(
            name="Cape Town",
            country="South Africa",
            description="A beautiful coastal city.",
            category="city",
            climate="mediterranean",
            best_time_to_visit="October to March",
            avg_daily_cost=1500,
            latitude=-33.9249,
            longitude=18.4241,
        )

        self.itinerary = Itinerary.objects.create(
            title="Cape Town Adventure",
            description="A five-day trip around Cape Town.",
            destination=self.destination,
            owner=self.user,
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 5),
            budget=10000,
            status="planning",
            is_public=True,
        )

        self.accommodation = Accommodation.objects.create(
            name="Cape Town Hotel",
            destination=self.destination,
            accommodation_type="hotel",
            description="A comfortable hotel.",
            price_per_night=1200,
            max_guests=2,
            amenities="WiFi, Breakfast, Pool",
            address="Cape Town CBD",
            contact_email="hotel@example.com",
            contact_phone="0211234567",
            is_available=True,
        )

        self.activity = Activity.objects.create(
            name="Table Mountain Hike",
            destination=self.destination,
            category="adventure",
            description="A guided hike up Table Mountain.",
            duration_hours=4,
            price=500,
            max_participants=10,
            requirements="Comfortable shoes and water.",
            is_available=True,
        )

    def test_accommodation_serializer(self):
        serializer = AccommodationSerializer(
            self.accommodation
        )

        data = serializer.data

        self.assertEqual(
            data["name"],
            "Cape Town Hotel",
        )

        self.assertEqual(
            data["destination"],
            self.destination.id,
        )

        self.assertEqual(
            data["max_guests"],
            2,
        )

    def test_activity_serializer(self):
        serializer = ActivitySerializer(
            self.activity
        )

        data = serializer.data

        self.assertEqual(
            data["name"],
            "Table Mountain Hike",
        )

        self.assertEqual(
            data["destination"],
            self.destination.id,
        )

        self.assertEqual(
            data["max_participants"],
            10,
        )

    def test_booking_serializer_includes_nested_accommodation(self):
        booking = Booking.objects.create(
            user=self.user,
            itinerary=self.itinerary,
            accommodation=self.accommodation,
            booking_date=date(2026, 10, 1),
            quantity=2,
            price=2400,
            status="pending",
        )

        serializer = BookingSerializer(booking)
        data = serializer.data

        self.assertIn(
            "accommodation",
            data,
        )
        self.assertEqual(
            data["accommodation"],
            self.accommodation.id,
        )

        self.assertEqual(
            data["accommodation_details"]["id"],
            self.accommodation.id,
        )

        self.assertEqual(
            data["accommodation_details"]["name"],
            "Cape Town Hotel",
        )

    def test_booking_serializer_includes_nested_activity(self):
        booking = Booking.objects.create(
            user=self.user,
            itinerary=self.itinerary,
            activity=self.activity,
            booking_date=date(2026, 10, 2),
            quantity=2,
            price=1000,
            status="pending",
        )

        serializer = BookingSerializer(booking)
        data = serializer.data

        self.assertIn(
            "activity",
            data,
        )
        self.assertEqual(
            data["activity"],
            self.activity.id,
        )

        self.assertEqual(
            data["activity_details"]["id"],
            self.activity.id,
        )

        self.assertEqual(
            data["activity_details"]["name"],
            "Table Mountain Hike",
        )

    def test_booking_create_serializer_accepts_accommodation_booking(
        self,
    ):
        data = {
            "user": self.user.id,
            "itinerary": self.itinerary.id,
            "accommodation": self.accommodation.id,
            "booking_date": "2026-10-01",
            "quantity": 2,
            "price": "2400.00",
            "status": "pending",
        }

        serializer = BookingCreateSerializer(
            data=data
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_booking_create_serializer_rejects_missing_booking_target(
        self,
    ):
        data = {
            "user": self.user.id,
            "itinerary": self.itinerary.id,
            "booking_date": "2026-10-01",
            "quantity": 1,
            "price": "1000.00",
            "status": "pending",
        }

        serializer = BookingCreateSerializer(
            data=data
        )

        self.assertFalse(
            serializer.is_valid()
        )

    def test_booking_create_serializer_rejects_both_targets(
        self,
    ):
        data = {
             "user": self.user.id,
             "itinerary": self.itinerary.id,
             "accommodation": self.accommodation.id,
             "activity": self.activity.id,
             "booking_date": "2026-10-01",
             "quantity": 1,
             "price": "1000.00",
             "status": "pending",
        }

        serializer = BookingCreateSerializer(
            data=data
        )

        self.assertFalse(
            serializer.is_valid()
        )
        self.assertIn(
            "non_field_errors",
            serializer.errors,
        )

    
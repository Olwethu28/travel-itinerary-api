from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase

from destinations.models import Destination

from .models import Itinerary
from .serializers import (
    ItineraryCreateUpdateSerializer,
    ItineraryDetailSerializer,
    ItineraryListSerializer,
)


User = get_user_model()


class ItinerarySerializerTests(TestCase):

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

    def test_itinerary_list_serializer(self):
        serializer = ItineraryListSerializer(self.itinerary)
        data = serializer.data

        self.assertEqual(data["title"], "Cape Town Adventure")
        self.assertEqual(data["status"], "planning")

    def test_itinerary_detail_serializer(self):
        serializer = ItineraryDetailSerializer(self.itinerary)
        data = serializer.data

        self.assertEqual(data["title"], "Cape Town Adventure")

        # Destination is represented as a nested object.
        self.assertEqual(
            data["destination"]["id"],
            self.destination.id,
        )

        self.assertEqual(
            data["destination"]["name"],
            "Cape Town",
        )

        self.assertEqual(
            data["owner"],
            self.user.id,
        )

    def test_itinerary_create_serializer_accepts_valid_data(self):
        data = {
            "title": "Durban Holiday",
            "description": "A relaxing trip to Durban.",
            "destination_id": self.destination.id,
            "owner": self.user.id,
            "start_date": "2026-11-01",
            "end_date": "2026-11-05",
            "budget": "8000.00",
            "status": "planning",
            "is_public": True,
        }

        serializer = ItineraryCreateUpdateSerializer(data=data)

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_itinerary_create_serializer_rejects_end_date_before_start_date(self):
        data = {
            "title": "Invalid Trip",
            "description": "Invalid dates.",
            "destination_id": self.destination.id,
            "owner": self.user.id,
            "start_date": "2026-11-10",
            "end_date": "2026-11-05",
            "budget": "8000.00",
            "status": "planning",
            "is_public": True,
        }

        serializer = ItineraryCreateUpdateSerializer(data=data)

        self.assertFalse(serializer.is_valid())

        self.assertTrue(
            "non_field_errors" in serializer.errors
            or "end_date" in serializer.errors
        )

    def test_itinerary_create_serializer_rejects_invalid_budget(self):
        data = {
            "title": "Invalid Budget Trip",
            "description": "Invalid budget.",
            "destination_id": self.destination.id,
            "owner": self.user.id,
            "start_date": "2026-11-01",
            "end_date": "2026-11-05",
            "budget": "-500.00",
            "status": "planning",
            "is_public": True,
        }

        serializer = ItineraryCreateUpdateSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("budget", serializer.errors)

    def test_itinerary_can_be_updated(self):
        data = {
            "title": "Updated Cape Town Adventure",
            "description": "Updated trip description.",
            "destination_id": self.destination.id,
            "owner": self.user.id,
            "start_date": "2026-10-01",
            "end_date": "2026-10-07",
            "budget": "15000.00",
            "status": "booked",
            "is_public": False,
        }

        serializer = ItineraryCreateUpdateSerializer(
            instance=self.itinerary,
            data=data,
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        itinerary = serializer.save()

        self.assertEqual(
            itinerary.title,
            "Updated Cape Town Adventure",
        )

        self.assertEqual(
            itinerary.status,
            "booked",
        )

        self.assertEqual(
            itinerary.budget,
            15000,
        )

    def test_itinerary_detail_serializer_includes_computed_fields(self):
        serializer = ItineraryDetailSerializer(self.itinerary)
        data = serializer.data

        self.assertIn("duration_days", data)
        self.assertIn("budget_remaining", data)
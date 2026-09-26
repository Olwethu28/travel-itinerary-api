from datetime import date

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from destinations.models import Destination
from .models import Itinerary


User = get_user_model()


class ItineraryListCreateViewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="Password123!",
        )

        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
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
            title="Cape Town Trip",
            description="A trip to Cape Town.",
            destination=self.destination,
            owner=self.user,
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 7),
            budget=10000,
        )

        self.url = reverse("itinerary-list-create")

    def test_authenticated_user_can_list_itineraries(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

    def test_user_only_sees_their_own_itineraries(self):
        Itinerary.objects.create(
            title="Other User Trip",
            description="Another trip.",
            destination=self.destination,
            owner=self.other_user,
            start_date=date(2026, 11, 1),
            end_date=date(2026, 11, 7),
            budget=5000,
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        titles = [
            itinerary["title"]
            for itinerary in response.data["results"]
        ]

        self.assertIn("Cape Town Trip", titles)
        self.assertNotIn("Other User Trip", titles)

    def test_unauthenticated_user_cannot_list_itineraries(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_user_can_create_itinerary(self):
        self.client.force_authenticate(user=self.user)

        data = {
            "title": "Durban Trip",
            "description": "A trip to Durban.",
            "destination_id": self.destination.id,
            "start_date": "2026-11-01",
            "end_date": "2026-11-07",
            "budget": 8000,
            "status": "planning",
            "is_public": False,
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        self.assertTrue(
            Itinerary.objects.filter(
                title="Durban Trip",
                owner=self.user,
            ).exists()
        )

    def test_unauthenticated_user_cannot_create_itinerary(self):
        data = {
            "title": "Durban Trip",
            "description": "A trip to Durban.",
            "destination_id": self.destination.id,
            "start_date": "2026-11-01",
            "end_date": "2026-11-07",
            "budget": 8000,
            "status": "planning",
            "is_public": False,
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
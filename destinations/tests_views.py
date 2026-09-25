from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Destination


class DestinationViewTests(APITestCase):

    def setUp(self):
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

    def test_can_list_destinations(self):
        url = reverse("destination-list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data["results"]),
            1,
        )

        self.assertEqual(
            response.data["results"][0]["name"],
            "Cape Town",
        )

    def test_can_retrieve_destination(self):
        url = reverse(
            "destination-detail",
            kwargs={"pk": self.destination.pk},
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["name"],
            "Cape Town",
        )

        self.assertIn(
            "average_rating",
            response.data,
        )

    def test_destination_list_uses_list_serializer(self):
        url = reverse("destination-list")

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertNotIn(
            "location",
            response.data["results"][0],
        )

    def test_destination_detail_uses_detail_serializer(self):
        url = reverse(
            "destination-detail",
            kwargs={"pk": self.destination.pk},
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "location",
            response.data,
        )

    def test_cannot_create_destination(self):
        url = reverse("destination-list")

        data = {
            "name": "Durban",
            "country": "South Africa",
            "description": "A coastal city.",
            "category": "city",
            "climate": "subtropical",
            "best_time_to_visit": "Summer",
            "avg_daily_cost": 1200,
            "latitude": -29.8587,
            "longitude": 31.0218,
        }

        response = self.client.post(url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_cannot_delete_destination(self):
        url = reverse(
            "destination-detail",
            kwargs={"pk": self.destination.pk},
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
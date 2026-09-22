from django.test import TestCase

from .models import Destination
from .serializers import (
    DestinationCreateUpdateSerializer,
    DestinationDetailSerializer,
    DestinationListSerializer,
)


class DestinationSerializerTests(TestCase):

    def setUp(self):
        self.destination = Destination.objects.create(
            name="Cape Town",
            country="South Africa",
            description="A beautiful coastal city.",
            category="CITY",
            climate="MEDITERRANEAN",
            latitude=-33.9249,
            longitude=18.4241,
        )

    def test_destination_list_serializer(self):
        serializer = DestinationListSerializer(self.destination)

        self.assertEqual(serializer.data["name"], "Cape Town")
        self.assertEqual(serializer.data["country"], "South Africa")

    def test_destination_detail_serializer_includes_computed_fields(self):
        serializer = DestinationDetailSerializer(self.destination)

        data = serializer.data

        self.assertIn("average_rating", data)
        self.assertIn("review_count", data)
        self.assertIn("total_itineraries", data)
        self.assertIn("total_accommodations", data)
        self.assertIn("total_activities", data)

    def test_destination_representation_contains_location(self):
        serializer = DestinationDetailSerializer(self.destination)

        data = serializer.data

        self.assertIn("location", data)
        self.assertEqual(data["location"]["latitude"], -33.9249)
        self.assertEqual(data["location"]["longitude"], 18.4241)

    def test_invalid_latitude_is_rejected(self):
        data = {
            "name": "Invalid Place",
            "country": "South Africa",
            "description": "Invalid coordinates.",
            "category": "CITY",
            "climate": "MEDITERRANEAN",
            "latitude": 100,
            "longitude": 18.4241,
        }

        serializer = DestinationCreateUpdateSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("latitude", serializer.errors)

    def test_invalid_longitude_is_rejected(self):
        data = {
            "name": "Invalid Place",
            "country": "South Africa",
            "description": "Invalid coordinates.",
            "category": "CITY",
            "climate": "MEDITERRANEAN",
            "latitude": -33.9249,
            "longitude": 200,
        }

        serializer = DestinationCreateUpdateSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("longitude", serializer.errors)

    def test_valid_destination_can_be_created(self):
        data = {
            "name": "Durban",
            "country": "South Africa",
            "description": "A coastal city.",
            "category": "CITY",
            "climate": "SUBTROPICAL",
            "latitude": -29.8587,
            "longitude": 31.0218,
        }

        serializer = DestinationCreateUpdateSerializer(data=data)

        self.assertTrue(serializer.is_valid(), serializer.errors)

        destination = serializer.save()

        self.assertEqual(destination.name, "Durban")
        self.assertEqual(destination.country, "South Africa")

    def test_destination_can_be_updated(self):
        serializer = DestinationCreateUpdateSerializer(
            instance=self.destination,
            data={
                "name": "Cape Town Updated",
                "country": "South Africa",
                "description": "Updated description.",
                "category": "CITY",
                "climate": "MEDITERRANEAN",
                "latitude": -33.9249,
                "longitude": 18.4241,
            },
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        destination = serializer.save()

        self.assertEqual(destination.name, "Cape Town Updated")
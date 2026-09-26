from datetime import date

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from destinations.models import Destination
from itineraries.models import Itinerary

from .models import Accommodation, Activity, Booking


User = get_user_model()


class BookingListCreateViewTests(APITestCase):

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

        self.accommodation = Accommodation.objects.create(
            name="Cape Town Hotel",
            destination=self.destination,
            accommodation_type="hotel",
            description="A comfortable hotel.",
            price_per_night=1200,
            max_guests=2,
            amenities="WiFi, breakfast",
            address="Cape Town",
            contact_email="hotel@example.com",
            contact_phone="0123456789",
            is_available=True,
        )

        self.activity = Activity.objects.create(
            name="Table Mountain Hike",
            destination=self.destination,
            category="adventure",
            description="A hike up Table Mountain.",
            duration_hours=4,
            price=500,
            max_participants=10,
            requirements="Comfortable shoes",
            is_available=True,
        )

        self.booking = Booking.objects.create(
            user=self.user,
            itinerary=self.itinerary,
            accommodation=self.accommodation,
            booking_date=date(2026, 9, 26),
            quantity=1,
            price=1200,
        )

        self.url = reverse("booking-list-create")

    def test_authenticated_user_can_list_bookings(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

    def test_user_only_sees_their_own_bookings(self):
        other_itinerary = Itinerary.objects.create(
            title="Other User Trip",
            description="Another trip.",
            destination=self.destination,
            owner=self.other_user,
            start_date=date(2026, 11, 1),
            end_date=date(2026, 11, 7),
            budget=5000,
        )

        Booking.objects.create(
            user=self.other_user,
            itinerary=other_itinerary,
            accommodation=self.accommodation,
            booking_date=date(2026, 9, 26),
            quantity=1,
            price=1200,
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data["results"]), 1)

        self.assertEqual(
            response.data["results"][0]["id"],
            self.booking.id,
        )

    def test_unauthenticated_user_cannot_list_bookings(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_user_can_create_accommodation_booking(self):
        self.client.force_authenticate(user=self.user)

        data = {
            "itinerary": self.itinerary.id,
            "accommodation": self.accommodation.id,
            "booking_date": "2026-10-01",
            "quantity": 2,
            "price": 2400,
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
            Booking.objects.filter(
                user=self.user,
                itinerary=self.itinerary,
                accommodation=self.accommodation,
                quantity=2,
            ).exists()
        )

    def test_authenticated_user_can_create_activity_booking(self):
        self.client.force_authenticate(user=self.user)

        data = {
            "itinerary": self.itinerary.id,
            "activity": self.activity.id,
            "booking_date": "2026-10-02",
            "quantity": 2,
            "price": 1000,
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
            Booking.objects.filter(
                user=self.user,
                itinerary=self.itinerary,
                activity=self.activity,
                quantity=2,
            ).exists()
        )

    def test_unauthenticated_user_cannot_create_booking(self):
        data = {
            "itinerary": self.itinerary.id,
            "accommodation": self.accommodation.id,
            "booking_date": "2026-10-01",
            "quantity": 1,
            "price": 1200,
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
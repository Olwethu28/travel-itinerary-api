from datetime import date

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from destinations.models import Destination
from itineraries.models import Itinerary

from .models import Budget, Expense


User = get_user_model()


class BudgetListCreateViewTests(APITestCase):

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

        self.budget = Budget.objects.create(
            itinerary=self.itinerary,
            accommodation_budget=3000,
            activities_budget=2000,
            food_budget=1500,
            transport_budget=1000,
            shopping_budget=500,
            miscellaneous_budget=500,
        )

        self.url = reverse("budget-list-create")

    def test_authenticated_user_can_list_budgets(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

    def test_user_only_sees_budgets_for_their_itineraries(self):
        other_itinerary = Itinerary.objects.create(
            title="Other User Trip",
            description="Another trip.",
            destination=self.destination,
            owner=self.other_user,
            start_date=date(2026, 11, 1),
            end_date=date(2026, 11, 7),
            budget=5000,
        )

        Budget.objects.create(
            itinerary=other_itinerary,
            accommodation_budget=1000,
            activities_budget=1000,
            food_budget=1000,
            transport_budget=1000,
            shopping_budget=500,
            miscellaneous_budget=500,
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data["results"]), 1)

        self.assertEqual(
            response.data["results"][0]["id"],
            self.budget.id,
        )

    def test_unauthenticated_user_cannot_list_budgets(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_user_can_create_budget(self):
        new_itinerary = Itinerary.objects.create(
            title="Durban Trip",
            description="A trip to Durban.",
            destination=self.destination,
            owner=self.user,
            start_date=date(2026, 12, 1),
            end_date=date(2026, 12, 7),
            budget=9000,
        )

        self.client.force_authenticate(user=self.user)

        data = {
            "itinerary": new_itinerary.id,
            "accommodation_budget": 2500,
            "activities_budget": 1500,
            "food_budget": 1500,
            "transport_budget": 1000,
            "shopping_budget": 500,
            "miscellaneous_budget": 500,
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
            Budget.objects.filter(
                itinerary=new_itinerary,
            ).exists()
        )

    def test_user_cannot_create_budget_for_another_users_itinerary(self):
        other_itinerary = Itinerary.objects.create(
            title="Other User Trip",
            description="Another trip.",
            destination=self.destination,
            owner=self.other_user,
            start_date=date(2026, 11, 1),
            end_date=date(2026, 11, 7),
            budget=5000,
        )

        self.client.force_authenticate(user=self.user)

        data = {
            "itinerary": other_itinerary.id,
            "accommodation_budget": 1000,
            "activities_budget": 1000,
            "food_budget": 1000,
            "transport_budget": 1000,
            "shopping_budget": 500,
            "miscellaneous_budget": 500,
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )


class ExpenseListCreateViewTests(APITestCase):

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

        self.expense = Expense.objects.create(
            itinerary=self.itinerary,
            category="food",
            description="Dinner",
            amount=350,
            date=date(2026, 10, 2),
            notes="Dinner at the waterfront",
        )

        self.url = reverse("expense-list-create")

    def test_authenticated_user_can_list_expenses(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

    def test_user_only_sees_expenses_for_their_itineraries(self):
        other_itinerary = Itinerary.objects.create(
            title="Other User Trip",
            description="Another trip.",
            destination=self.destination,
            owner=self.other_user,
            start_date=date(2026, 11, 1),
            end_date=date(2026, 11, 7),
            budget=5000,
        )

        Expense.objects.create(
            itinerary=other_itinerary,
            category="transport",
            description="Taxi",
            amount=200,
            date=date(2026, 11, 2),
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

        self.assertEqual(
            response.data["results"][0]["id"],
            self.expense.id,
        )

    def test_authenticated_user_can_create_expense(self):
        self.client.force_authenticate(user=self.user)

        data = {
            "itinerary": self.itinerary.id,
            "category": "food",
            "description": "Lunch",
            "amount": 250,
            "date": "2026-10-03",
            "notes": "Lunch during sightseeing",
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
            Expense.objects.filter(
                itinerary=self.itinerary,
                description="Lunch",
            ).exists()
        )

    def test_user_cannot_create_expense_for_another_users_itinerary(self):
        other_itinerary = Itinerary.objects.create(
            title="Other User Trip",
            description="Another trip.",
            destination=self.destination,
            owner=self.other_user,
            start_date=date(2026, 11, 1),
            end_date=date(2026, 11, 7),
            budget=5000,
        )

        self.client.force_authenticate(user=self.user)

        data = {
            "itinerary": other_itinerary.id,
            "category": "food",
            "description": "Lunch",
            "amount": 250,
            "date": "2026-11-02",
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_unauthenticated_user_cannot_create_expense(self):
        data = {
            "itinerary": self.itinerary.id,
            "category": "food",
            "description": "Lunch",
            "amount": 250,
            "date": "2026-10-03",
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
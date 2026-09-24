from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase

from destinations.models import Destination
from itineraries.models import Itinerary

from .models import Budget, Expense
from .serializers import BudgetSerializer, ExpenseSerializer


User = get_user_model()


class BudgetSerializerTests(TestCase):

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

        self.budget = Budget.objects.create(
            itinerary=self.itinerary,
            accommodation_budget=3000,
            activities_budget=2000,
            food_budget=1500,
            transport_budget=1000,
            shopping_budget=500,
            miscellaneous_budget=500,
        )

        self.expense = Expense.objects.create(
            itinerary=self.itinerary,
            category="food",
            description="Restaurant dinner",
            amount=450,
            date=date(2026, 10, 2),
            notes="Dinner in Cape Town",
        )

    def test_budget_serializer(self):
        serializer = BudgetSerializer(self.budget)
        data = serializer.data

        self.assertEqual(
            data["itinerary"],
            self.itinerary.id,
        )

        self.assertEqual(
            data["accommodation_budget"],
            "3000.00",
        )

        self.assertEqual(
            data["food_budget"],
            "1500.00",
        )

    def test_budget_serializer_calculates_total_budget(self):
        serializer = BudgetSerializer(self.budget)
        data = serializer.data

        self.assertIn(
            "total_budget",
            data,
        )

        self.assertEqual(
            data["total_budget"],
            8500,
        )

    def test_budget_serializer_accepts_valid_data(self):
        new_itinerary = Itinerary.objects.create(
            title="Durban Trip",
            description="A trip to Durban.",
            destination=self.destination,
            owner=self.user,
            start_date=date(2026, 11, 1),
            end_date=date(2026, 11, 7),
            budget=10000,
            status="planning",
        )

        data = {
            "itinerary": new_itinerary.id,
            "accommodation_budget": "3000.00",
            "activities_budget": "2000.00",
            "food_budget": "1500.00",
            "transport_budget": "1000.00",
            "shopping_budget": "500.00",
            "miscellaneous_budget": "500.00",
        }

        serializer = BudgetSerializer(data=data)

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        budget = serializer.save()

        self.assertEqual(
            budget.itinerary,
            new_itinerary,
        )

        self.assertEqual(
            budget.accommodation_budget,
            3000,
        )

    def test_budget_serializer_rejects_negative_budget(self):
        data = {
            "itinerary": self.itinerary.id,
            "accommodation_budget": "-100.00",
            "activities_budget": "2000.00",
            "food_budget": "1500.00",
            "transport_budget": "1000.00",
            "shopping_budget": "500.00",
            "miscellaneous_budget": "500.00",
        }

        serializer = BudgetSerializer(data=data)

        self.assertFalse(
            serializer.is_valid()
        )

        self.assertIn(
            "accommodation_budget",
            serializer.errors,
        )

    def test_budget_can_be_updated(self):
        data = {
            "itinerary": self.itinerary.id,
            "accommodation_budget": "5000.00",
            "activities_budget": "2500.00",
            "food_budget": "2000.00",
            "transport_budget": "1200.00",
            "shopping_budget": "600.00",
            "miscellaneous_budget": "700.00",
        }

        serializer = BudgetSerializer(
            instance=self.budget,
            data=data,
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        budget = serializer.save()

        self.assertEqual(
            budget.accommodation_budget,
            5000,
        )

    def test_expense_serializer(self):
        serializer = ExpenseSerializer(self.expense)
        data = serializer.data

        self.assertEqual(
            data["itinerary"],
            self.itinerary.id,
        )

        self.assertEqual(
            data["category"],
            "food",
        )

        self.assertEqual(
            data["description"],
            "Restaurant dinner",
        )

    def test_expense_serializer_rejects_invalid_amount(self):
        data = {
            "itinerary": self.itinerary.id,
            "category": "food",
            "description": "Invalid expense",
            "amount": "-50.00",
            "date": "2026-10-03",
            "notes": "Invalid amount",
        }

        serializer = ExpenseSerializer(data=data)

        self.assertFalse(
            serializer.is_valid()
        )

        self.assertIn(
            "amount",
            serializer.errors,
        )
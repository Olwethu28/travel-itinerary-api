from rest_framework import serializers

from .models import Budget, Expense


class BudgetSerializer(
    serializers.ModelSerializer
):
    """Serializer for itinerary budgets."""

    total_budget = serializers.ReadOnlyField()

    itinerary_title = serializers.CharField(
        source="itinerary.title",
        read_only=True,
    )

    class Meta:
        model = Budget

        fields = [
            "id",
            "itinerary",
            "itinerary_title",
            "accommodation_budget",
            "activities_budget",
            "food_budget",
            "transport_budget",
            "shopping_budget",
            "miscellaneous_budget",
            "total_budget",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "itinerary_title",
            "total_budget",
            "created_at",
            "updated_at",
        ]

    def validate(self, data):
        """Validate budget values."""

        budget_fields = [
            "accommodation_budget",
            "activities_budget",
            "food_budget",
            "transport_budget",
            "shopping_budget",
            "miscellaneous_budget",
        ]

        for field in budget_fields:
            value = data.get(field)

            if value is not None and value < 0:
                raise serializers.ValidationError(
                    {
                        field:
                        "Budget amount cannot be negative."
                    }
                )

        return data

    def create(self, validated_data):
        """Create a budget."""
        return Budget.objects.create(
            **validated_data
        )


class ExpenseSerializer(
    serializers.ModelSerializer
):
    """Serializer for individual expenses."""

    itinerary_title = serializers.CharField(
        source="itinerary.title",
        read_only=True,
    )

    class Meta:
        model = Expense

        fields = [
            "id",
            "itinerary",
            "itinerary_title",
            "category",
            "description",
            "amount",
            "date",
            "receipt",
            "notes",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "itinerary_title",
            "created_at",
        ]

    def validate_amount(self, value):
        """Ensure expense amount is positive."""
        if value < 0:
            raise serializers.ValidationError(
                "Expense amount cannot be negative."
            )

        return value

    def validate(self, data):
        """Validate expense description."""
        description = data.get("description")

        if description and not description.strip():
            raise serializers.ValidationError(
                {
                    "description":
                    "Description cannot be empty."
                }
            )

        return data

    def update(self, instance, validated_data):
        """Update an expense."""
        return super().update(
            instance,
            validated_data,
        )
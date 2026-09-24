from rest_framework import serializers

from destinations.models import Destination
from .models import (
    Itinerary,
    DailyPlan,
    Collaboration,
)


class CollaborationSerializer(
    serializers.ModelSerializer
):
    """Serializer for itinerary collaborators."""

    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    class Meta:
        model = Collaboration
        fields = [
            "id",
            "user",
            "username",
            "email",
            "role",
            "invited_at",
        ]

        read_only_fields = [
            "id",
            "invited_at",
        ]

    def validate(self, data):
        """Validate collaboration data."""
        itinerary = data.get("itinerary")
        user = data.get("user")

        if itinerary and itinerary.owner == user:
            raise serializers.ValidationError(
                "The itinerary owner cannot be added as a collaborator."
            )

        return data


class DailyPlanSerializer(
    serializers.ModelSerializer
):
    """Daily itinerary plan with computed information."""

    activities_count = serializers.SerializerMethodField()

    class Meta:
        model = DailyPlan
        fields = [
            "id",
            "itinerary",
            "day_number",
            "date",
            "title",
            "notes",
            "activities",
            "activities_count",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "activities_count",
        ]

    def get_activities_count(self, obj):
        return obj.activities.count()

    def validate_day_number(self, value):
        """Ensure day number is positive."""
        if value < 1:
            raise serializers.ValidationError(
                "Day number must be at least 1."
            )

        return value


class ItineraryListSerializer(
    serializers.ModelSerializer
):
    """Lightweight itinerary representation."""

    destination_name = serializers.CharField(
        source="destination.name",
        read_only=True,
    )

    owner_username = serializers.CharField(
        source="owner.username",
        read_only=True,
    )

    duration_days = serializers.ReadOnlyField()

    budget_remaining = serializers.ReadOnlyField()

    class Meta:
        model = Itinerary
        fields = [
            "id",
            "title",
            "destination",
            "destination_name",
            "owner",
            "owner_username",
            "start_date",
            "end_date",
            "duration_days",
            "budget",
            "budget_remaining",
            "status",
            "is_public",
        ]

        read_only_fields = [
            "id",
            "owner",
            "duration_days",
            "budget_remaining",
        ]


class ItineraryDetailSerializer(
    serializers.ModelSerializer
):
    """Detailed itinerary with nested relationships."""

    destination = serializers.SerializerMethodField()

    daily_plans = DailyPlanSerializer(
        many=True,
        read_only=True,
    )

    collaborations = CollaborationSerializer(
        many=True,
        read_only=True,
    )

    bookings_count = serializers.SerializerMethodField()

    expenses_count = serializers.SerializerMethodField()

    duration_days = serializers.ReadOnlyField()

    budget_remaining = serializers.ReadOnlyField()

    class Meta:
        model = Itinerary

        fields = [
            "id",
            "title",
            "description",
            "destination",
            "owner",
            "daily_plans",
            "collaborations",
            "bookings_count",
            "expenses_count",
            "start_date",
            "end_date",
            "duration_days",
            "budget",
            "actual_spent",
            "budget_remaining",
            "status",
            "is_public",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "owner",
            "daily_plans",
            "collaborations",
            "bookings_count",
            "expenses_count",
            "duration_days",
            "budget_remaining",
            "created_at",
            "updated_at",
        ]

    def get_destination(self, obj):
        return {
            "id": obj.destination.id,
            "name": obj.destination.name,
            "country": obj.destination.country,
            "category": obj.destination.category,
            "climate": obj.destination.climate,
        }

    def get_bookings_count(self, obj):
        return obj.bookings.count()

    def get_expenses_count(self, obj):
        return obj.expenses.count()

    def validate(self, data):
        """Validate itinerary dates and budget."""

        start_date = data.get("start_date")
        end_date = data.get("end_date")
        budget = data.get("budget")

        if start_date and end_date:
            if end_date < start_date:
                raise serializers.ValidationError(
                    {
                        "end_date":
                        "End date must be after start date."
                    }
                )

        if budget is not None and budget < 0:
            raise serializers.ValidationError(
                {
                    "budget":
                    "Budget cannot be negative."
                }
            )

        return data

    def create(self, validated_data):
        """Create itinerary and its budget."""

        itinerary = Itinerary.objects.create(
            **validated_data
        )

        from budgets.models import Budget

        Budget.objects.create(
            itinerary=itinerary
        )

        return itinerary

    def to_representation(self, instance):
        """Customize itinerary output."""
        representation = super().to_representation(
            instance
        )

        representation["budget_status"] = (
            "within_budget"
            if instance.budget_remaining >= 0
            else "over_budget"
        )

        return representation


class ItineraryCreateUpdateSerializer(
    serializers.ModelSerializer
):
    """Serializer for creating and updating itineraries."""

    destination_id = serializers.PrimaryKeyRelatedField(
        queryset=Destination.objects.all(),
        source="destination",
    )

    class Meta:
        model = Itinerary

        fields = [
          "title",
          "description",
          "destination_id",
          "start_date",
          "end_date",
          "budget",
          "status",
          "is_public",
        ]

    def validate(self, data):
        """Validate itinerary dates."""
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if start_date and end_date:
            if end_date < start_date:
                raise serializers.ValidationError(
                    {
                        "end_date":
                        "End date must be after start date."
                    }
                )

        return data

    def validate_budget(self, value):
        """Ensure budget is greater than zero."""
        if value <= 0:
            raise serializers.ValidationError(
                "Budget must be greater than zero."
            )

        return value

    def update(self, instance, validated_data):
        """Update an itinerary."""
        return super().update(
            instance,
            validated_data,
        )
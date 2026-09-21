from rest_framework import serializers

from .models import (
    Accommodation,
    Activity,
    Booking,
)


class AccommodationSerializer(
    serializers.ModelSerializer
):
    """Serializer for accommodation."""

    destination_name = serializers.CharField(
        source="destination.name",
        read_only=True,
    )

    booking_count = serializers.SerializerMethodField()

    class Meta:
        model = Accommodation

        fields = [
            "id",
            "name",
            "destination",
            "destination_name",
            "accommodation_type",
            "description",
            "price_per_night",
            "max_guests",
            "amenities",
            "address",
            "contact_email",
            "contact_phone",
            "image",
            "is_available",
            "booking_count",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "destination_name",
            "booking_count",
            "created_at",
        ]

    def get_booking_count(self, obj):
        return obj.bookings.count()

    def validate_price_per_night(self, value):
        """Ensure accommodation price is positive."""
        if value < 0:
            raise serializers.ValidationError(
                "Price cannot be negative."
            )

        return value

    def validate_max_guests(self, value):
        """Ensure at least one guest is allowed."""
        if value < 1:
            raise serializers.ValidationError(
                "Maximum guests must be at least 1."
            )

        return value

    def to_representation(self, instance):
        """Customize accommodation response."""
        representation = super().to_representation(
            instance
        )

        representation["availability"] = (
            "available"
            if instance.is_available
            else "unavailable"
        )

        return representation


class ActivitySerializer(
    serializers.ModelSerializer
):
    """Serializer for activities."""

    destination_name = serializers.CharField(
        source="destination.name",
        read_only=True,
    )

    booking_count = serializers.SerializerMethodField()

    class Meta:
        model = Activity

        fields = [
            "id",
            "name",
            "destination",
            "destination_name",
            "category",
            "description",
            "duration_hours",
            "price",
            "max_participants",
            "requirements",
            "image",
            "is_available",
            "booking_count",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "destination_name",
            "booking_count",
            "created_at",
        ]

    def get_booking_count(self, obj):
        return obj.bookings.count()

    def validate_duration_hours(self, value):
        """Validate activity duration."""
        if value <= 0:
            raise serializers.ValidationError(
                "Duration must be greater than zero."
            )

        return value


class BookingSerializer(
    serializers.ModelSerializer
):
    """Detailed booking serializer."""

    user_username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    accommodation_details = (
        AccommodationSerializer(
            source="accommodation",
            read_only=True,
        )
    )

    activity_details = ActivitySerializer(
        source="activity",
        read_only=True,
    )

    booking_target = serializers.SerializerMethodField()

    class Meta:
        model = Booking

        fields = [
            "id",
            "user",
            "user_username",
            "itinerary",
            "accommodation",
            "accommodation_details",
            "activity",
            "activity_details",
            "booking_target",
            "status",
            "booking_date",
            "quantity",
            "price",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "user",
            "user_username",
            "accommodation_details",
            "activity_details",
            "booking_target",
            "created_at",
            "updated_at",
        ]

    def get_booking_target(self, obj):
        if obj.accommodation:
            return {
                "type": "accommodation",
                "id": obj.accommodation.id,
                "name": obj.accommodation.name,
            }

        if obj.activity:
            return {
                "type": "activity",
                "id": obj.activity.id,
                "name": obj.activity.name,
            }

        return None

    def validate(self, data):
        """Ensure exactly one booking target exists."""

        accommodation = data.get("accommodation")
        activity = data.get("activity")

        if not accommodation and not activity:
            raise serializers.ValidationError(
                "Booking must have an accommodation or activity."
            )

        if accommodation and activity:
            raise serializers.ValidationError(
                "Booking cannot have both accommodation and activity."
            )

        return data

    def create(self, validated_data):
        """Create a booking for the authenticated user."""

        request = self.context.get("request")

        if request and request.user.is_authenticated:
            validated_data["user"] = request.user

        return Booking.objects.create(
            **validated_data
        )


class BookingCreateSerializer(
    serializers.ModelSerializer
):
    """Serializer specifically for creating bookings."""

    class Meta:
        model = Booking

        fields = [
            "itinerary",
            "accommodation",
            "activity",
            "booking_date",
            "quantity",
            "price",
        ]

    def validate(self, data):
        """Validate booking target."""

        if bool(data.get("accommodation")) == bool(
            data.get("activity")
        ):
            raise serializers.ValidationError(
                "Choose exactly one: accommodation or activity."
            )

        return data
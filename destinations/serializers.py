from rest_framework import serializers

from .models import Destination


class DestinationBaseSerializer(
    serializers.ModelSerializer
):
    """Base destination serializer."""

    class Meta:
        model = Destination
        fields = [
            "id",
            "name",
            "country",
            "description",
            "category",
            "climate",
            "best_time_to_visit",
            "avg_daily_cost",
            "image",
            "latitude",
            "longitude",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class DestinationListSerializer(
    DestinationBaseSerializer
):
    """Lightweight serializer for destination lists."""

    average_rating = serializers.ReadOnlyField()

    review_count = serializers.SerializerMethodField()

    class Meta(DestinationBaseSerializer.Meta):
        fields = [
            "id",
            "name",
            "country",
            "category",
            "climate",
            "avg_daily_cost",
            "image",
            "average_rating",
            "review_count",
        ]

        read_only_fields = [
            "id",
            "average_rating",
            "review_count",
        ]

    def get_review_count(self, obj):
        return obj.reviews.count()


class DestinationDetailSerializer(
    DestinationBaseSerializer
):
    """Detailed destination serializer."""

    average_rating = serializers.ReadOnlyField()

    total_itineraries = serializers.SerializerMethodField()

    total_accommodations = serializers.SerializerMethodField()

    total_activities = serializers.SerializerMethodField()

    class Meta(DestinationBaseSerializer.Meta):
        fields = DestinationBaseSerializer.Meta.fields + [
            "average_rating",
            "total_itineraries",
            "total_accommodations",
            "total_activities",
        ]

        read_only_fields = [
            "id",
            "average_rating",
            "total_itineraries",
            "total_accommodations",
            "total_activities",
            "created_at",
            "updated_at",
        ]

    def get_total_itineraries(self, obj):
        return obj.itineraries.count()

    def get_total_accommodations(self, obj):
        return obj.accommodations.count()

    def get_total_activities(self, obj):
        return obj.activities.count()

    def to_representation(self, instance):
        """Customize the detailed response."""
        representation = super().to_representation(
            instance
        )

        representation["location"] = {
            "latitude": representation.pop("latitude"),
            "longitude": representation.pop("longitude"),
        }

        return representation


class DestinationCreateUpdateSerializer(
    DestinationBaseSerializer
):
    """Create and update destinations."""

    def validate_name(self, value):
        """Validate destination name."""
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Destination name must contain at least 2 characters."
            )

        return value.strip()

    def validate(self, data):
        """Validate destination coordinates."""
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        if latitude is not None:
            if latitude < -90 or latitude > 90:
                raise serializers.ValidationError(
                    {"latitude": "Latitude must be between -90 and 90."}
                )

        if longitude is not None:
            if longitude < -180 or longitude > 180:
                raise serializers.ValidationError(
                    {"longitude": "Longitude must be between -180 and 180."}
                )

        return data

    def create(self, validated_data):
        """Create a destination."""
        return Destination.objects.create(
            **validated_data
        )

    def update(self, instance, validated_data):
        """Update a destination."""
        return super().update(
            instance,
            validated_data,
        )
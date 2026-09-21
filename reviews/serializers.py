from rest_framework import serializers

from .models import Review


class ReviewSerializer(
    serializers.ModelSerializer
):
    """Serializer for reviews."""

    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    target_name = serializers.SerializerMethodField()

    class Meta:
        model = Review

        fields = [
            "id",
            "user",
            "username",
            "destination",
            "accommodation",
            "activity",
            "rating",
            "title",
            "content",
            "visit_date",
            "images",
            "helpful_count",
            "target_name",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "user",
            "username",
            "helpful_count",
            "target_name",
            "created_at",
            "updated_at",
        ]

    def get_target_name(self, obj):
        if obj.destination:
            return obj.destination.name

        if obj.accommodation:
            return obj.accommodation.name

        if obj.activity:
            return obj.activity.name

        return None

    def validate_rating(self, value):
        """Ensure rating is between 1 and 5."""
        if value < 1 or value > 5:
            raise serializers.ValidationError(
                "Rating must be between 1 and 5."
            )

        return value

    def validate(self, data):
        """Ensure exactly one review target exists."""

        targets = [
            data.get("destination"),
            data.get("accommodation"),
            data.get("activity"),
        ]

        if sum(target is not None for target in targets) != 1:
            raise serializers.ValidationError(
                "A review must target exactly one item."
            )

        return data

    def create(self, validated_data):
        """Create a review for the authenticated user."""

        request = self.context.get("request")

        if request and request.user.is_authenticated:
            validated_data["user"] = request.user

        return Review.objects.create(
            **validated_data
        )
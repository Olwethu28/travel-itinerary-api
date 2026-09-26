from rest_framework import generics, permissions

from .models import Itinerary
from .serializers import (
    ItineraryCreateUpdateSerializer,
    ItineraryListSerializer,
)


class ItineraryListCreateView(generics.ListCreateAPIView):
    """
    List the authenticated user's itineraries
    and create a new itinerary.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Itinerary.objects
            .select_related("destination", "owner")
            .prefetch_related("daily_plans", "collaborations")
            .filter(owner=self.request.user)
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ItineraryCreateUpdateSerializer

        return ItineraryListSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
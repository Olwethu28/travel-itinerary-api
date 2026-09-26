from rest_framework import generics, permissions

from .models import Booking
from .serializers import BookingCreateSerializer, BookingSerializer


class BookingListCreateView(generics.ListCreateAPIView):
    """
    List the authenticated user's bookings
    and create a new booking.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Booking.objects
            .select_related(
                "user",
                "itinerary",
                "accommodation",
                "activity",
            )
            .filter(user=self.request.user)
            .order_by("-created_at")
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return BookingCreateSerializer

        return BookingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
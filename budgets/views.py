from rest_framework import generics, permissions

from .models import Budget, Expense
from .serializers import BudgetSerializer, ExpenseSerializer


class BudgetListCreateView(generics.ListCreateAPIView):
    """
    List the budgets belonging to the authenticated user's itineraries
    and create a budget for one of those itineraries.
    """

    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Budget.objects
            .select_related("itinerary", "itinerary__owner")
            .filter(itinerary__owner=self.request.user)
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        itinerary = serializer.validated_data["itinerary"]

        if itinerary.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied(
                "You can only create budgets for your own itineraries."
            )

        serializer.save()


class ExpenseListCreateView(generics.ListCreateAPIView):
    """
    List expenses belonging to the authenticated user's itineraries
    and create a new expense.
    """

    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Expense.objects
            .select_related("itinerary", "itinerary__owner")
            .filter(itinerary__owner=self.request.user)
            .order_by("-date", "-created_at")
        )

    def perform_create(self, serializer):
        itinerary = serializer.validated_data["itinerary"]

        if itinerary.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied(
                "You can only create expenses for your own itineraries."
            )

        serializer.save()
from rest_framework import permissions, viewsets

from .models import Destination
from .serializers import (
    DestinationDetailSerializer,
    DestinationListSerializer,
)


class DestinationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View destinations.

    Supports:
    - GET /destinations/
    - GET /destinations/<id>/
    """

    queryset = Destination.objects.all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return DestinationDetailSerializer

        return DestinationListSerializer
from django.urls import path

from .views import ItineraryListCreateView


urlpatterns = [
    path(
        "itineraries/",
        ItineraryListCreateView.as_view(),
        name="itinerary-list-create",
    ),
]
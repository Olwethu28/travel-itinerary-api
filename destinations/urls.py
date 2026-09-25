from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DestinationViewSet


router = DefaultRouter()

router.register(
    "destinations",
    DestinationViewSet,
    basename="destination",
)

urlpatterns = [
    path("", include(router.urls)),
]
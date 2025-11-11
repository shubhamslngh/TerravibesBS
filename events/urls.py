from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet,
    VendorViewSet,
    ContentViewSet,
    EventPackageViewSet,
    InquiryViewSet,
    BookingViewSet,
    RegisterAPI,
    LoginAPI,
    GuideViewSet,
    MoodViewSet,
    seed_package,
    generate_package,  
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"vendors", VendorViewSet)
router.register(r"content", ContentViewSet, basename="content")
router.register(r"packages", EventPackageViewSet, basename="packages")
router.register(r"inquiries", InquiryViewSet, basename="inquiries")
router.register(r"bookings", BookingViewSet, basename="bookings")
router.register(r"guides", GuideViewSet, basename="guides")
router.register(r"moods", MoodViewSet, basename="moods")


# Combine router and custom endpoints
urlpatterns = [
    path("", include(router.urls)),  # includes all viewsets
    path("auth/register/", RegisterAPI.as_view(), name="auth-register"),
    path("auth/login/", LoginAPI.as_view(), name="auth-login"),
    path(
        "seed-package/", seed_package, name="seed_package"
    ),  # ✅ custom seeding endpoint
    path(
        "generate-package/", generate_package, name="generate_package"
    ),  
]

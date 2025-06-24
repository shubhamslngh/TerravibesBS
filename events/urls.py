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
)

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"vendors", VendorViewSet)
router.register(r"content", ContentViewSet, basename="content")
router.register(r"packages", EventPackageViewSet, basename="packages")
router.register(r"inquiries", InquiryViewSet, basename="inquiries")
router.register(r"bookings", BookingViewSet, basename="bookings")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/register/", RegisterAPI.as_view(), name="auth-register"),
    path("auth/login/", LoginAPI.as_view(), name="auth-login"),
]

from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import generics,viewsets, permissions
from django.contrib.auth import get_user_model
from .models import Vendor, Content, EventPackage, Inquiry, Booking
from .serializers import (
    UserSerializer,
    VendorSerializer,
    ContentSerializer,
    EventPackageSerializer,
    InquirySerializer,
    BookingSerializer,
    RegisterSerializer,
    LoginSerializer,
)
from events.models import Guide
from events.serializers import GuideSerializer

User = get_user_model()


class RegisterAPI(generics.CreateAPIView):
    """
    POST /api/auth/register/
    {
      "username": "...",
      "email": "...",
      "password": "...",
      "phone": "..."
    }
    """

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class GuideViewSet(viewsets.ModelViewSet):
    """
    list:    GET /api/guides/
    retrieve: GET /api/guides/{pk}/
    create:  POST /api/guides/           (admin only)
    update:  PUT/PATCH /api/guides/{pk}/ (admin only)
    delete:  DELETE /api/guides/{pk}/    (admin only)
    """

    queryset = Guide.objects.prefetch_related("packages")
    serializer_class = GuideSerializer

    def get_permissions(self):
        # read‐only for everyone; write for admins
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class LoginAPI(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    permission_classes = [permissions.IsAdminUser]


class ContentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Content.objects.order_by("-publish_date")
    serializer_class = ContentSerializer
    permission_classes = [permissions.AllowAny]


class EventPackageViewSet(viewsets.ModelViewSet):
    queryset = EventPackage.objects.all()
    serializer_class = EventPackageSerializer

    def get_permissions(self):
        if self.request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class InquiryViewSet(viewsets.ModelViewSet):
    queryset = Inquiry.objects.all()
    serializer_class = InquirySerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

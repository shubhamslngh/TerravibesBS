from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import generics,viewsets, permissions
from django.contrib.auth import get_user_model
from .models import Vendor, Content, EventPackage, Inquiry, Booking, Mood
from .serializers import (
    UserSerializer,
    VendorSerializer,
    ContentSerializer,
    EventPackageSerializer,
    InquirySerializer,
    BookingSerializer,
    RegisterSerializer,
    LoginSerializer,
    MoodSerializer
)
from events.models import Guide
from events.serializers import GuideSerializer
from django.conf import settings
import google.generativeai as genai
import re
genai.configure(api_key=settings.GEMINI_API_KEY)
User = get_user_model()
from rest_framework.decorators import api_view, permission_classes
from .models import EventPackage
from .serializers import EventPackageSerializer
import json


@api_view(["POST"])
@permission_classes([permissions.AllowAny])  # You can restrict to IsAdminUser later
def seed_package(request):
    """
    POST /api/seed-package/
    Accepts JSON payload for creating EventPackage entries.
    Example payload:
    {
        "title": "Hills Cottage - Private Pool Villa",
        "description": "...",
        "price": "40000.00",
        "services": [
            {"name": "Drinks", "description": "Premium bar"},
            {"name": "Food", "description": "Multi-cuisine"},
            {"name": "DJ", "description": "Professional sound setup"}
        ],
        "images": [
            {"media_file": "uploads/swimming.avif", "title": "Swimming", "body": "Pool"},
            {"media_file": "uploads/castle.avif", "title": "Cottage", "body": "View"}
        ],
        "moods": []
    }
    """
    try:
        data = request.data

        # Handle if 'services' or 'images' are strings instead of arrays
        if isinstance(data.get("services"), str):
            try:
                data["services"] = json.loads(data["services"])
            except json.JSONDecodeError:
                data["services"] = []

        if isinstance(data.get("images"), str):
            try:
                data["images"] = json.loads(data["images"])
            except json.JSONDecodeError:
                data["images"] = []

        serializer = EventPackageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Package seeded successfully!", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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


class ContentViewSet(viewsets.ModelViewSet):
    serializer_class = ContentSerializer

    def get_permissions(self):
        # ✅ Allow anyone to GET or POST (temporary for development)
        if self.request.method in ["GET", "POST"]:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def get_queryset(self):
        queryset = Content.objects.all().order_by("-publish_date")
        content_type = self.request.query_params.get("content_type")
        slug = self.request.query_params.get("slug")

        if content_type:
            queryset = queryset.filter(content_type=content_type)
        if slug:
            queryset = queryset.filter(slug=slug)

        return queryset


class MoodViewSet(viewsets.ModelViewSet):
    queryset = Mood.objects.all().order_by("name")
    serializer_class = MoodSerializer
    permission_classes = [permissions.AllowAny]


class EventPackageViewSet(viewsets.ModelViewSet):
    queryset = EventPackage.objects.all()
    serializer_class = EventPackageSerializer

    def get_permissions(self):
        if self.request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            return [permissions.AllowAny()]
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

import os, json, re
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
import google.generativeai as genai
from .models import EventPackage
from .serializers import EventPackageSerializer
from events.models import Mood, Guide  # assuming you have these models

genai.configure(api_key=settings.GEMINI_API_KEY)

import os, json, re
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
import google.generativeai as genai
from events.models import Mood, Guide  # assuming they exist


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def generate_package(request):
    """
    POST /api/generate-package/
    {
      "messages": [
        {"role": "user", "content": "I want to make a luxury yoga retreat in Rishikesh."},
        {"role": "assistant", "content": "..."},
        {"role": "user", "content": "Now please give the final JSON package."}
      ]
    }

    Returns conversational response or final JSON when asked.
    """

    messages = request.data.get("messages", [])
    if not messages:
        return Response({"error": "Messages list is required."}, status=400)

    # Fetch context for grounding
    available_moods = list(Mood.objects.values_list("name", flat=True))
    available_guides = list(Guide.objects.values_list("name", flat=True))

    context_info = f"""
    Available moods: {', '.join(available_moods) or 'None'}
    Available guides: {', '.join(available_guides) or 'None'}

    You are a helpful conversational travel package designer.
    - give price in number only for the json
    - On normal conversation, respond naturally no need for json when the context seems to be enough for generation then provide json.
    - whatever moods is given by the user search simillar from available moods and use them.
    - In json response please give pk values for moods and guides from the available lists.
    - If image is selected then selct other wise keep empty.
    - give response in json
    {{
      "title": "",
      "description": "",
      "price": "",
      "services": [{{"name": "", "description": ""}}],
      "images": [{{"media_file": "", "title": "", "body": ""}}],
      "moods": [],
      "guides": []
    }}
    """

    try:    
        gemini_history = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
        if role == "assistant":
            gemini_history.append({"role": "model", "parts": [content]})
        else:
            gemini_history.append({"role": "user", "parts": [content]})

        model = genai.GenerativeModel("gemini-2.5-flash")
        chat = model.start_chat(history=gemini_history)
        response = chat.send_message(context_info)

        # Detect if the assistant produced JSON (user explicitly asked)
        match = re.search(r"\{.*\}", response.text, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group(0))
                return Response({"mode": "json", "data": parsed})
            except Exception:
                return Response({"mode": "json", "raw": response.text})

        # Otherwise, it’s normal conversation
        return Response(
            {
                "mode": "chat",
                "reply": response.text,
            }
        )

    except Exception as e:
        return Response({"error": str(e)}, status=500)


def generate_image_caption(image_path):
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = "Write a short poetic description for this image suitable for a luxury travel blog."
    with open(image_path, "rb") as f:
        img = {"mime_type": "image/png", "data": f.read()}
    response = model.generate_content([prompt, img])
    return response.text.strip()

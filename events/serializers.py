from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from .models import Vendor, Content, EventPackage, Inquiry, Booking, Guide
from rest_framework.authtoken.models import Token


User = get_user_model()
class GuideSerializer(serializers.ModelSerializer):
    # Show a nested list of package IDs or titles:
    packages = serializers.PrimaryKeyRelatedField(
        many=True, queryset=EventPackage.objects.all()
    )

    class Meta:
        model = Guide
        fields = ["id", "name", "bio", "photo", "expertise", "packages"]


class RegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "phone",
        ]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        # Lookup user by email
        try:
            user_obj = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"non_field_errors": ["Invalid credentials"]}, code="authorization"
            )

        # Authenticate using username
        user = authenticate(username=user_obj.username, password=password)
        if not user:
            raise serializers.ValidationError(
                {"non_field_errors": ["Invalid credentials"]}, code="authorization"
            )

        token, created = Token.objects.get_or_create(user=user)
        return {"email": user.email, "token": token.key}


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "phone", "profile_picture", "role"]
        read_only_fields = ["id", "role"]


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = "__all__"


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = "__all__"


class EventPackageSerializer(serializers.ModelSerializer):
    images = ContentSerializer(many=True, read_only=True)
    guides = GuideSerializer(many=True, read_only=True)

    class Meta:
        model = EventPackage
        fields = [
            "id",
            "title",
            "description",
            "price",
            "services",
            "images",
            "is_active",
            "moods",
            "guides",
        ]


class InquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = "__all__"
        read_only_fields = ["id", "status", "created_at", "updated_at"]


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "id",
            "first_name",
            "last_name",
            "gender",
            "country",
            "date_of_birth",
            "address",
            "name",
            "email",
            "phone",
            "package",
            "start_date",
            "end_date",
            "status",
        ]

    def create(self, validated_data):
        if not validated_data.get("name"):
            validated_data["name"] = (
                f"{validated_data.get('first_name', '')} {validated_data.get('last_name', '')}"
            )
        return super().create(validated_data)

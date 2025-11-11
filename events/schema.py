import graphene
from graphene import relay, ObjectType, Field, List, Boolean, Float, String, Int
from graphene_django.types import DjangoObjectType
from django.db.models import Q
from .models import EventPackage, Mood, Content, Guide


# --- MODELS TO GRAPHQL TYPES ---


class MoodType(DjangoObjectType):
    id = graphene.Int()
    class Meta:
        model = Mood
        fields = ("id", "name", "description", "icon")


class GuideType(DjangoObjectType):
    id = graphene.Int()
    class Meta:
        model = Guide
        fields = ("id", "name", "bio", "expertise", "photo")


class ContentType(DjangoObjectType):
    class Meta:
        model = Content
        fields = ("id", "src", "title", "body")


class EventPackageType(DjangoObjectType):
    id = graphene.Int()
    moods = List(MoodType)
    guides = List(GuideType)
    images = List(ContentType)

    class Meta:
        model = EventPackage
        fields = (
            "id",
            "title",
            "description",
            "price",
            "services",
            "is_active",
        )

    # ✅ Explicit resolvers (important for ManyToMany)
    def resolve_moods(self, info):
        return self.moods.all()

    def resolve_guides(self, info):
        return self.guides.all()

    def resolve_images(self, info):
        return self.images.all()


# --- QUERY ROOT ---


class Query(ObjectType):
    packages = List(
        EventPackageType,
        mood=String(required=False),
        min_price=Float(required=False),
        max_price=Float(required=False),
        is_active=Boolean(required=False),
    )
    package = Field(EventPackageType, id=Int(required=True))

    def resolve_packages(
        self, info, mood=None, min_price=None, max_price=None, is_active=None
    ):
        qs = EventPackage.objects.all().distinct()

        if is_active is not None:
            qs = qs.filter(is_active=is_active)
        if min_price is not None:
            qs = qs.filter(price__gte=min_price)
        if max_price is not None:
            qs = qs.filter(price__lte=max_price)
        if mood:
            qs = qs.filter(moods__name__icontains=mood)

        return qs

    def resolve_package(self, info, id):
        return EventPackage.objects.filter(pk=id).first()


schema = graphene.Schema(query=Query)

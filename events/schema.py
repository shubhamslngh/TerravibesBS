import graphene
from graphene import relay, ObjectType, Field, List, Boolean, Float, String, Int
from graphene_django.types import DjangoObjectType
from django.db.models import Q
from .models import EventPackage, Mood, Content


class MoodType(DjangoObjectType):
    class Meta:
        model = Mood
        fields = ("id", "name")


class EventPackageType(DjangoObjectType):
    moods = List(MoodType)

    class Meta:
        model = EventPackage
        fields = (
            "id",
            "title",
            "description",
            "price",
            "services",
            "is_active",
            "images",  # if you have a related ContentType you can expose it similarly
        )

    def resolve_moods(self, info):
        return self.moods.all()


class ContentType(DjangoObjectType):
    class Meta:
        model = Content
        fields = (
            "id",
            "media_file",
            "title",
            "body",
        )


class MoodType(DjangoObjectType):
    class Meta:
        model = Mood
        fields = ("id", "name")


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
            # case-insensitive match on related Mood name
            qs = qs.filter(moods__name__iexact=mood)

        return qs

    def resolve_package(self, info, id):
        try:
            return EventPackage.objects.get(pk=id)
        except EventPackage.DoesNotExist:
            return None


schema = graphene.Schema(query=Query)

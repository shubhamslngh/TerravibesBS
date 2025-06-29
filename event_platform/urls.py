from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from events.schema import schema  # your GraphQL schema

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("events.urls")),  # REST
    path("graphql/", csrf_exempt(GraphQLView.as_view(schema=schema, graphiql=True))),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

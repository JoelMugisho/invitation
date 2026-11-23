from pathlib import Path

from django.urls import path
from django.views.static import serve
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from donnees.views import (
    a_propos,
    accueil,
    billetterie,
    collecte,
    invitations,
    marketplace,
    organiser,
    petition,
)

VISUELS = Path(__file__).resolve().parents[1] / "donnees" / "static" / "donnees"


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok", "service": "invitations"})


urlpatterns = [
    path("", accueil),
    path("organiser", organiser),
    path("invitations", invitations),
    path("billetterie", billetterie),
    path("collecte", collecte),
    path("petition", petition),
    path("marketplace", marketplace),
    path("a-propos", a_propos),
    path("health", health),
    path("visuels/<path:path>", serve, {"document_root": VISUELS}),
]

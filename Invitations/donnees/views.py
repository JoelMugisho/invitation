from django.shortcuts import render


def _page(request, template, page):
    return render(request, template, {"page": page})


def accueil(request):
    return _page(request, "donnees/accueil.html", "accueil")


def organiser(request):
    return _page(request, "donnees/organiser.html", "organiser")


def invitations(request):
    return _page(request, "donnees/invitations.html", "invitations")


def billetterie(request):
    return _page(request, "donnees/billetterie.html", "billetterie")


def collecte(request):
    return _page(request, "donnees/collecte.html", "collecte")


def petition(request):
    return _page(request, "donnees/petition.html", "petition")


def marketplace(request):
    return _page(request, "donnees/marketplace.html", "marketplace")


def a_propos(request):
    return _page(request, "donnees/a-propos.html", "a-propos")

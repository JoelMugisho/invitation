from django.shortcuts import render


def accueil(request):
    return render(request, "donnees/accueil.html")

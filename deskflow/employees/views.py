from django.http import HttpResponse
from django.shortcuts import render

# Создавайте свои представления здесь.


def index(request):
    return HttpResponse("<h1>Страница по сотрудникам</h1>")

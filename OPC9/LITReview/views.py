from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm

# Create your views here.

def login(request):
    return render(request, 'index.html', {})

def register(response):
    form = UserCreationForm()
    return render(response, 'register.html', {"form":form})

def profile(request):
    return render(request, 'profile.html', {})

def flux(request):
    return render(request, 'flux.html', {})
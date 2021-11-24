from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

# Create your views here.

def home(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            login(request, user)

    return render(request, 'index.html', {"form":form})

def register(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/')

    return render(request, 'register.html', {"form":form})

def profile(request):
    return render(request, 'profile.html', {})

def flux(request):
    return render(request, 'flux.html', {})
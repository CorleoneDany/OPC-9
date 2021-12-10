from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.views.generic import TemplateView

from .forms import ReviewForm, TicketForm
from .models import Ticket, Review, User
from django.db.models import CharField, Value

from itertools import chain

# Create your views here.


def home(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        print(form)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('flux')

    return render(request, 'index.html', {"form": form})


def register(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/')

    return render(request, 'register.html', {"form": form})


def disconnect(request):
    logout(request)
    return redirect('/')


def profile(request):
    reviews = get_users_viewable_reviews(request.user)
    # returns queryset of reviews
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))

    tickets = get_users_viewable_tickets(request.user)
    # returns queryset of tickets
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))

    # combine and sort the two types of posts
    posts = sort_posts(reviews, tickets)
    print(posts)

    return render(request, 'profile.html', {'posts': posts})


def create_review(request, id_review=None):
    review_instance = Review.objects.get(
        id_review) if id_review is not None else None
    if request.method == 'GET':
        form = ReviewForm(instance=review_instance)
        return render(request, 'create_review.html', {"form": form})

    elif request.method == 'POST':
        form = ReviewForm(data=request.POST, instance=review_instance)
        if form.is_valid():
            validated_form = form.save(commit=False)
            validated_form.user = request.user
            validated_form.save()
            return redirect('flux')
    return render(request, 'create_review.html', {"form": form})


def create_ticket(request, id_article=None):
    ticket_instance = Ticket.objects.get(
        id_article) if id_article is not None else None
    if request.method == 'GET':
        form = TicketForm(instance=ticket_instance)
        return render(request, 'create_ticket.html', {"form": form})

    elif request.method == 'POST':
        form = TicketForm(data=request.POST)
        if form.is_valid():
            validated_form = form.save(commit=False)
            validated_form.user = request.user
            validated_form.save()
            return redirect('flux')
    return render(request, 'create_ticket.html', {"form": form})


def flux(request):

    posts = get_all_posts()
    return render(request, 'flux.html', {"posts": posts})


def get_all_posts():
    reviews = Review.objects.all()
    tickets = Ticket.objects.all()
    return sort_posts(reviews, tickets)


def sort_posts(reviews, tickets):
    return sorted(
        chain(reviews, tickets),
        key=lambda post: post.time_created,
        reverse=True
    )


def print_all_posts(reviews, tickets):
    print(sort_posts(reviews, tickets))

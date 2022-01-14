from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.views.generic import TemplateView
from django.db.models import CharField, Value
import pprint


from .forms import ReviewForm, TicketForm, UserFollowsForm
from .models import Ticket, Review, User, UserFollows
from django.db.models import CharField, Value

from itertools import chain

# Create your views here.


def home(request):
    if request.user.is_authenticated:
        return redirect('/flux')

    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            connect_user(request, form)
            return redirect('flux')

    return render(request, 'index.html', {"form": form})


def connect_user(request, form):
    username = form.cleaned_data.get('username')
    password = form.cleaned_data.get('password')
    user = authenticate(username=username, password=password)
    login(request, user)


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
    reviews = get_user_reviews(request)
    tickets = get_user_posts(request)
    posts = sort_posts(reviews, tickets)

    return render(request, 'profile.html', {'posts': posts})


def update_review(request, id_review=None):
    review_instance = Review.objects.get(
        pk=id_review)
    ticket_instance = Ticket.objects.get(
        pk=review_instance.ticket.id)

    if request.method == 'GET' and ticket_instance:
        review_form = ReviewForm(instance=review_instance)
        review_id = review_instance.id
        post = ticket_instance
        return render(request, 'update_review.html', {"review_form": review_form, "post": post, "review_id": review_id})

    elif request.method == 'POST':
        review_form = ReviewForm(data=request.POST, instance=review_instance)
        if review_form.is_valid():
            review_form.save()
            return redirect('flux')


def respond_to_ticket(request, id_ticket=None):
    post = Ticket.objects.get(pk=id_ticket)
    review_form = ReviewForm()

    if request.method == 'GET':
        ticket_id = post.id
        return render(request, 'review_respond.html', {"review_form": review_form, "post": post, 'ticket_id': ticket_id})

    if request.method == 'POST':
        review_form = ReviewForm(data=request.POST)
        if review_form.is_valid():
            validated_review = review_form.save(commit=False)
            validated_review.ticket_id = post.id
            validated_review.user = request.user
            validated_review.save()
            return redirect('flux')


def create_review(request):
    review_form = ReviewForm()
    ticket_form = TicketForm()

    # create review and ticket
    if request.method == 'POST':
        review_form = ReviewForm(data=request.POST)
        ticket_form = TicketForm(data=request.POST)
        if review_form.is_valid() and ticket_form.is_valid():
            save_new_review(ticket_form, request, review_form)
            return redirect('flux')

    return render(request, 'create_review.html', {"review_form": review_form, "ticket_form": ticket_form})


def save_new_review(ticket_form, request, review_form):
    validated_ticket = ticket_form.save(commit=False)
    validated_ticket.user = request.user
    validated_ticket.save()
    validated_review = review_form.save(commit=False)
    validated_review.ticket = Ticket.objects.last()
    validated_review.user = request.user
    validated_review.save()


def create_ticket(request, id_ticket=None):
    ticket_instance = Ticket.objects.get(
        pk=id_ticket) if id_ticket is not None else None
    if request.method == 'GET':
        form = TicketForm(instance=ticket_instance)
        return render(request, 'create_ticket.html', {"form": form})

    elif request.method == 'POST':
        form = TicketForm(data=request.POST)
        if form.is_valid():
            save_ticket(request, form)
            return redirect('flux')
    return render(request, 'create_ticket.html', {"form": form})


def update_ticket(request, id_ticket=None):
    ticket_instance = Ticket.objects.get(
        pk=id_ticket) if id_ticket is not None else None
    if request.method == 'GET':
        ticket_form = TicketForm(instance=ticket_instance)
        ticket_id = ticket_instance.id
        return render(request, 'update_ticket.html', {"ticket_form": ticket_form, "ticket_id": ticket_id})

    elif request.method == 'POST':
        ticket_form = TicketForm(data=request.POST, instance=ticket_instance)
        if ticket_form.is_valid():
            ticket_form.save()
            return redirect('flux')


def save_ticket(request, form):
    validated_form = form.save(commit=False)
    validated_form.user = request.user
    validated_form.save()


def flux(request):
    posts = get_all_posts()
    return render(request, 'flux.html', {"posts": posts})


def get_all_posts():
    reviews = Review.objects.all()
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))

    tickets = Ticket.objects.all()
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))

    tickets_id_list = [review.ticket.id for review in reviews]

    for ticket in tickets:
        ticket.responded = ticket.id in tickets_id_list
    return sort_posts(reviews, tickets)


def sort_posts(reviews, tickets):
    return sorted(
        chain(reviews, tickets),
        key=lambda post: post.time_created,
        reverse=True
    )


def get_user_posts(request):
    return Ticket.objects.filter(user=request.user)


def get_user_reviews(request):
    return Review.objects.filter(user=request.user)


def subscriptions(request):
    followers = return_all_followers(request)
    followings = return_all_followings(request)
    form = UserFollowsForm()
    if request.method == 'POST' and form.is_valid():
        validated_form = form.save(commit=False)
        validated_form.user = request.user
        validated_form.save()
        return redirect('flux')
    return render(request, 'subscriptions.html', {"form": form, "followers": followers, "followings": followings})


def return_all_followers(request):
    return UserFollows.objects.filter(followed_user=request.user)


def return_all_followings(request):
    followings = UserFollows.objects.filter(user=request.user)
    return [following.followed_user for following in followings]


def print_all_posts(reviews, tickets):
    print(sort_posts(reviews, tickets))

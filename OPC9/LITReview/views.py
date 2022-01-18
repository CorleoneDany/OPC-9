from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db.models import CharField, Value
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from .forms import ReviewForm, TicketForm, UserFollowsForm
from .models import Ticket, Review, User, UserFollows

from itertools import chain

# Create your views here.


def home(request):
    """Print the main page."""
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
    """Connect the user."""
    username = form.cleaned_data.get('username')
    password = form.cleaned_data.get('password')
    user = authenticate(username=username, password=password)
    login(request, user)


def register(request):
    """Register the user."""
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
    """Disconnect the user."""
    logout(request)
    return redirect('/')


@login_required
def profile(request):
    """Render the users posts."""
    reviews = get_user_reviews(request)
    tickets = get_user_tickets(request)
    posts = sort_posts(reviews, tickets)

    return render(request, 'profile.html', {'posts': posts})


@login_required
def update_review(request, id_review=None):
    """Update the chosen review."""
    review_instance = Review.objects.get(
        pk=id_review)
    ticket_instance = Ticket.objects.get(
        pk=review_instance.ticket.id)

    if request.method == 'GET' and ticket_instance:
        review_form = ReviewForm(instance=review_instance)
        review_id = review_instance.id
        post = ticket_instance
        return render(request, 'update_review.html',
                      {"review_form": review_form,
                          "post": post, "review_id": review_id}
                      )

    elif request.method == 'POST':
        review_form = ReviewForm(data=request.POST, instance=review_instance)
        if review_form.is_valid():
            review_form.save()
            return redirect('flux')


@login_required
def respond_to_ticket(request, id_ticket=None):
    """Respond to the chosen ticket."""
    post = Ticket.objects.get(pk=id_ticket)
    review_form = ReviewForm()

    if request.method == 'GET':
        ticket_id = post.id
        return render(request, 'review_respond.html',
                      {"review_form": review_form,
                          "post": post, 'ticket_id': ticket_id}
                      )

    if request.method == 'POST':
        review_form = ReviewForm(data=request.POST)
        if review_form.is_valid():
            validated_review = review_form.save(commit=False)
            validated_review.ticket_id = post.id
            validated_review.user = request.user
            validated_review.save()
            return redirect('flux')


@login_required
def create_review(request):
    """Create a review."""
    review_form = ReviewForm()
    ticket_form = TicketForm()

    # create review and ticket
    if request.method == 'POST':
        review_form = ReviewForm(data=request.POST)
        ticket_form = TicketForm(data=request.POST, files=request.FILES)
        if review_form.is_valid() and ticket_form.is_valid():
            save_new_review(ticket_form, request, review_form)
            return redirect('flux')

    return render(request, 'create_review.html',
                  {"review_form": review_form, "ticket_form": ticket_form})


def save_new_review(ticket_form, request, review_form):
    """Save the new review."""
    validated_ticket = ticket_form.save(commit=False)
    validated_ticket.user = request.user
    validated_ticket.save()
    validated_review = review_form.save(commit=False)
    validated_review.ticket = Ticket.objects.last()
    validated_review.user = request.user
    validated_review.save()


@login_required
def create_ticket(request, id_ticket=None):
    """Create a ticket."""
    ticket_instance = Ticket.objects.get(
        pk=id_ticket) if id_ticket is not None else None
    if request.method == 'GET':
        form = TicketForm(instance=ticket_instance)
        return render(request, 'create_ticket.html', {"form": form})

    elif request.method == 'POST':
        form = TicketForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            save_ticket(request, form)
            return redirect('flux')
    return render(request, 'create_ticket.html', {"form": form})


@login_required
def update_ticket(request, id_ticket=None):
    """Update the chosen ticket."""
    ticket_instance = Ticket.objects.get(
        pk=id_ticket) if id_ticket is not None else None
    if request.method == 'GET':
        ticket_form = TicketForm(instance=ticket_instance)
        ticket_id = ticket_instance.id
        return render(request, 'update_ticket.html',
                      {"ticket_form": ticket_form, "ticket_id": ticket_id})

    elif request.method == 'POST':
        ticket_form = TicketForm(
            data=request.POST, instance=ticket_instance, files=request.FILES)
        if ticket_form.is_valid():
            ticket_form.save()
            return redirect('flux')


@login_required
def save_ticket(request, form):
    """Save the chosen ticket."""
    validated_form = form.save(commit=False)
    validated_form.user = request.user
    validated_form.save()


@login_required
def flux(request):
    """Render the main menu."""
    posts = get_all_posts(request)
    return render(request, 'flux.html', {"posts": posts})


def get_all_posts(request):
    """Get all posts and sorts them."""
    followings = return_all_followings_list(request)

    reviews = Review.objects.filter(
        Q(user__in=followings) | Q(user=request.user))
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))

    tickets = Ticket.objects.filter(
        Q(user__in=followings) | Q(user=request.user))
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))

    tickets_id_list = [review.ticket.id for review in reviews]

    for ticket in tickets:
        ticket.responded = ticket.id in tickets_id_list
    return sort_posts(reviews, tickets)


def sort_posts(reviews, tickets):
    """Sort post."""
    return sorted(
        chain(reviews, tickets),
        key=lambda post: post.time_created,
        reverse=True
    )


@login_required
def get_user_tickets(request):
    """Get connected user's tickets."""
    return Ticket.objects.filter(user=request.user)


@login_required
def get_user_reviews(request):
    """Get connected user's reviews."""
    return Review.objects.filter(user=request.user)


@login_required
def subscriptions(request):
    """Render the subscriptions page."""
    followers = return_all_followers(request)
    followings = return_all_followings(request)
    form = UserFollowsForm
    if request.method == 'POST':
        following_username = request.POST['followed_user']
        following_instance = User.objects.filter(
            username=following_username).first()
        cleaned_post = {'followed_user': following_instance}
        form = UserFollowsForm(data=cleaned_post)
        if form.is_valid():
            validated_form = form.save(commit=False)
            validated_form.user = request.user
            validated_form.save()
            return redirect('flux')
    return render(request, 'subscriptions.html',
                  {"form": form, "followers": followers, "followings": followings})


@login_required
def return_all_followers(request):
    """Return all user's followers in user follow model."""
    return UserFollows.objects.filter(followed_user=request.user)


@login_required
def return_all_followings(request):
    """Return all user's followings in user follow model."""
    return UserFollows.objects.filter(user=request.user)


@login_required
def return_all_followings_list(request):
    """Return all user's followings."""
    return UserFollows.objects.filter(user=request.user).values_list('followed_user')


@login_required
def delete_subscription(request, id_following):
    """Delete chosen subscription."""
    following = UserFollows.objects.get(pk=id_following)
    following.delete()
    return redirect('flux')


@login_required
def delete_review(request, id_review):
    """Delete chosen review."""
    review = Review.objects.get(pk=id_review)
    review.delete()
    return redirect('flux')


@login_required
def delete_ticket(request, id_ticket):
    """Delete chosen ticket."""
    ticket = Ticket.objects.get(pk=id_ticket)
    ticket.delete()
    return redirect('flux')

from django.forms import forms, ModelForm

from .models import Review, Ticket, UserFollows


class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ['headline', 'rating', 'body']


class TicketForm(ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'image']


class UserFollows(ModelForm):
    class Meta:
        model = UserFollows
        fields = ['followed_user']

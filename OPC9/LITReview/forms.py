from django.forms import forms, ModelForm

from .models import Review, Ticket, UserFollows


class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ['headline', 'rating', 'body', 'user']
        labels = {'headline': 'Titre', 'rating': 'Note', 'body': 'Critique'}
        exclude = ['user']


class TicketForm(ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'user', 'image']
        labels = {'title': 'Titre',
                  'description': 'Description', 'image': 'Couverture'}
        exclude = ['user']


class UserFollows(ModelForm):
    class Meta:
        model = UserFollows
        fields = ['followed_user']

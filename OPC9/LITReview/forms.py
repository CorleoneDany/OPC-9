from django import forms
from django.forms import ModelForm

from .models import Review, Ticket, UserFollows


class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ['headline', 'rating', 'body', 'user']
        labels = {'headline': 'Titre', 'rating': 'Note', 'body': 'Critique'}
        exclude = ['user']
        rating_choices = [(1, '1'), (2, '2'),
                          (3, '3'), (4, '4'), (5, '5')]
        widgets = {'rating': forms.RadioSelect(choices=rating_choices)}


class TicketForm(ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'user', 'image']
        labels = {'title': 'Titre',
                  'description': 'Description', 'image': 'Couverture'}
        exclude = ['user']


class UserFollowsForm(ModelForm):
    class Meta:
        model = UserFollows
        fields = ['user', 'followed_user']
        labels = {'followed_user': 'Utilisateur à suivre :'}
        exclude = ['user']
        widgets = {'followed_user': forms.TextInput}

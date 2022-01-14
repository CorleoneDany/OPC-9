from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Ticket(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048, blank=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True,
                              upload_to='img')
    time_created = models.DateTimeField(auto_now_add=True)

    @property
    def type(self):
        return 'Ticket'

    def to_dict(self):
        return {
            'type': 'ticket',
            'title': self.title,
            'description': self.description,
            'user': self.user,
            'image': self.image,
            'time_created': self.time_created,
            'responded': ''
        }


class Review(models.Model):
    ticket = models.ForeignKey(to=Ticket, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        # validates that rating must be between 0 and 5
        validators=[MinValueValidator(0), MaxValueValidator(5)])
    headline = models.CharField(max_length=128)
    body = models.TextField(max_length=8192, blank=True)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)

    @property
    def type(self):
        return 'Review'

    @property
    def stars_count(self):
        return ['★' for _ in range(self.rating)]

    def to_dict(self):
        return {
            'type': 'review',
            'ticket': self.ticket.to_dict(),
            'rating': self.rating,
            'headline': self.headline,
            'body': self.body,
            'user': self.user,
            'time_created': self.time_created
        }


class UserFollows(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE,
                             related_name='followed_by')
    followed_user = models.ForeignKey(to=User, on_delete=models.CASCADE,
                                      related_name='followed_user')

    def to_dict(self):
        return {
            'user': self.user,
            'followed_user': self.followed_user
        }

    class Meta:
        # ensures we don't get multiple UserFollows instances
        # for unique user-user_followed pairs
        unique_together = ('user', 'followed_user', )

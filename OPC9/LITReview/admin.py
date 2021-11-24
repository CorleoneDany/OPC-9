from django.contrib import admin
from .models import Ticket, Review

# Register your models here.
models = [Ticket, Review]
admin.site.register(models)
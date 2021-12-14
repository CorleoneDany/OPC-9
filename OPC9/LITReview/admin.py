from django.contrib import admin
from .models import Ticket, Review, UserFollows

# Register your models here.


class SuperAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)


models = [Ticket, Review, UserFollows]
admin.site.register(models, SuperAdmin)

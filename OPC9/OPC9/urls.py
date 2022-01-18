"""OPC9 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from LITReview import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('logout/', views.disconnect, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('flux/', views.flux, name='flux'),
    path('subscriptions/', views.subscriptions, name='subscriptions'),
    path('new_ticket/', views.create_ticket, name='new_ticket'),
    path('update_ticket/<int:id_ticket>',
         views.update_ticket, name='update_ticket'),
    path('new_review/', views.create_review, name='new_review'),
    path('update_review/<int:id_review>',
         views.update_review, name='update_review'),
    path('review_respond/', views.respond_to_ticket, name='review_respond'),
    path('review_respond/<int:id_ticket>',
         views.respond_to_ticket, name='review_respond'),
    path('delete_subscription/<int:id_following>',
         views.delete_subscription, name='delete_subscription')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.conf import settings
from django.urls import path
from . import views

urlpatterns = [
    path('progress/', views.progress, name='progress'),
    path('process/', views.recognition, name='process'),
]

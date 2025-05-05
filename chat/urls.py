from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    # path('', views.index),
    path('user_register/',views.UserRegisterView.as_view()),
]

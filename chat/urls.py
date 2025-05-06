from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('', views.index),
    path("<str:room_name>/<int:id>/", views.room, name="room"),
    path('user_register/', views.UserRegisterView.as_view()),

]


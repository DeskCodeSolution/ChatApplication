from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.login),
    path("<str:room_name>/<int:id>/", views.room, name="room"),
    path("createroom/", views.createroom),
    path('user_register/', views.UserRegisterView.as_view()),
    path('user_login/', views.LoginView.as_view()),
    path('room_management/', views.RoomDataView.as_view())

]


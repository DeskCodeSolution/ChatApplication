from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('user_register/', views.UserRegisterView.as_view()),
    path('user_login/', views.LoginView.as_view()),
    path('user_logout/', views.LogoutView.as_view()),
    path('chat_history/', views.ChatHistory.as_view()),
    path('room_management/', views.RoomDataView.as_view()),


    path('register/', views.register),
    path('login/', views.login),
    # path("createroom/<int:user_id>/", views.createroom),
    # path("room/<str:room_id>/<int:room_id>/", views.room),

]


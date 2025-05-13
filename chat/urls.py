from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.login),
    path("<str:room_name>/<int:id>/", views.room),
    path("createroom/<str:user_name>/<int:user_id>/", views.createroom),
    path('user_register/', views.UserRegisterView.as_view()),
    path('user_login/', views.LoginView.as_view()),
    path('room_management/', views.RoomDataView.as_view()),
    path('LoadContentData/', views.LoadContentData.as_view()),
    path('user_logout/', views.LogoutView.as_view()),
    path('chat_history', views.ChatHistory.as_view()),
]


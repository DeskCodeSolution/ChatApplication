from django.urls import path
from .consumers import *

websocket_urlpatterns = [
    path("ws/chatroom/<str:room_name>/<int:user_id>/", ChatConsumer.as_asgi()),
]
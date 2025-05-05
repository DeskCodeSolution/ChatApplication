from django.urls import path
from .consumers import *

websocket_urlpatterns = [
    path("ws/chatroom/<chatroom_name>/<id>/", ChatroomConsumer.as_asgi()),
]
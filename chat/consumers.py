from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json
from .models import *

class ChatroomConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['chatroom_name']

        self.user_id = self.scope['url_route']['kwargs']['id']
        self.channel_layer = get_channel_layer()
        async_to_sync(self.channel_layer.group_add)(
            self.room_name,
            self.channel_name
            )

        self.accept()

        self.send(text_data=json.dumps({
        "msg": "connection established"
        }))

    def receive(self, text_data):
        username = UserMaster.objects.get(id = self.user_id).name
        text_data_json = json.loads(text_data)
        text_data_json['username'] = username

        room = RoomManagement.objects.get_or_create(
            roomId=self.room_name
        )[0]


        if room.message:
            current_messages = json.loads(room.message)
            if isinstance(current_messages, list):
                current_messages.append(text_data_json)
            else:
                current_messages = [current_messages, text_data_json]
            room.message = json.dumps(current_messages)
        else:
            room.message = json.dumps([text_data_json])
        room.save()


        async_to_sync(self.channel_layer.group_send)(
            self.room_name,
            {
                "type": "chat_message",
                "message": [text_data_json['message'], text_data_json['username']]
            }
        )

    def chat_message(self, event):
        self.send(text_data=json.dumps({
        'message':event['message']
        }))

    def disconnect(self, code):
        print("connection has been closed>>", code)









from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json
from .models import *

class ChatroomConsumer(WebsocketConsumer):
    def connect(self):
        print("self.scope>>", self.scope)
        print("self.path", self.scope['path'])

        self.room_name = self.scope['url_route']['kwargs']['chatroom_name']
        self.chatroom_name = f'chatroom_{self.room_name}'

        self.user_id = self.room_name = self.scope['url_route']['kwargs']['id']

        print("self.user_id", self.user_id)
        print("running this")
        print("room_name", self.room_name)
        print("chatroom_name", self.chatroom_name)

        self.channel_layer = get_channel_layer()
        print(f"Auto-generated channel_name: {self.channel_name}")


        async_to_sync(self.channel_layer.group_add)(
            self.chatroom_name,
            self.channel_name
        )


        self.accept()

        self.send(text_data=json.dumps({
        "msg": "connection established"
        }))

    def receive(self, text_data):
        print("data received from the client>>", text_data)

        username = UserMaster.objects.get(id = self.user_id).name
        print("username>>", username)

        text_data_json = json.loads(text_data)
        text_data_json['username'] = username
        print("text_data_json", text_data_json)

        # text_data_json {'message': 'what is your name', 'username': 'user1'}
        print("text_data_username", text_data_json['username'])
        print("text_data_message", text_data_json['message'])
        print("text_data_room_name", self.chatroom_name)


        user = UserMaster.objects.get(id=self.user_id)
        ChatManagement.objects.create(
        room_name=self.chatroom_name,
        message=text_data_json['message'],
        user_id=user
        )

        async_to_sync(self.channel_layer.group_send)(
            self.chatroom_name,
            {
                "type": "chat_message",
                "message": [text_data_json['message'], text_data_json['username']]
            }
        )

    def chat_message(self, event):
        print("chat_message")
        print("event>>", event)

        self.send(text_data=json.dumps({
        'msg':event['message']
        }))

    def disconnect(self, code):
        print("connection has been closed>>", code)









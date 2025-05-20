from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json
from .models import *
from django.utils import timezone
from .serializers import *
import datetime


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
        username = UserMaster.objects.get(id=self.user_id).name
        contact_users = ContactList.objects.filter(user_id=self.user_id).filter(room_id=self.room_name)
        text_data_json = json.loads(text_data)
        text_data_json['username'] = username
        now = datetime.datetime.now()
        text_data_json["time"] = now.strftime("%D:%H:%M:%S")
        contact_user = contact_users.first()

        if contact_user:
            if contact_user.message:
                current_messages = json.loads(contact_user.message)
                current_messages.append(text_data_json)
                contact_user.message = json.dumps(current_messages)
            else:
                contact_user.message = json.dumps([text_data_json])
            contact_user.save()

        # Store same data of chat on both sides

        room = RoomManagement.objects.get(id=self.room_name)
        users = room.users.all()

        userId = None
        user_id_list = []
        for user in users:
            user_id_list.append(user.id)
        for i in user_id_list:
            if i != int(self.user_id):
                userId = i
                break
        if userId:
            contact_user_2 = ContactList.objects.filter(user_id=userId).filter(room_id=self.room_name)
            user2 = contact_user_2.first()
            if user2:
                if user2.message:
                    current_messages1 = json.loads(user2.message)
                    current_messages1.append(text_data_json)
                    user2.message = json.dumps(current_messages1)
                else:
                    user2.message = json.dumps([text_data_json])
                user2.save()



        async_to_sync(self.channel_layer.group_send)(
            self.room_name,
            {
                "type": "chat_message",
                "message": text_data_json
            }
        )

    def chat_message(self, event):
        self.send(text_data=json.dumps({
        'message':event['message']
        }))

    def disconnect(self, code):
        print("connection has been closed>>", code)









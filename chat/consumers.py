
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .utils import generate
from .models import *
import uuid
from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer
import asyncio

class ChatConsumer(AsyncWebsocketConsumer):
    channel_layer = get_channel_layer()

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.user_id = self.scope['url_route']['kwargs']['user_id']

        print(self.room_name, self.user_id)

        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )

        print("scope", self.room_name)
        print("scope", self.user_id)

        await self.accept()

    async def receive(self, text_data=None):
        if text_data:
            data = json.loads(text_data)
            print("data", data)

            if data["event_type"] == "history":
                return await self.handle_message_history_data()

            response =  generate(data["message"])

            text_data_store = {"input":data["message"], "output":response}
            user = await sync_to_async(UserMaster.objects.get)(id = self.user_id)
            print(user)
            room, created = await sync_to_async(RoomManagement.objects.get_or_create)(room_id=self.room_name, user_id=user.id)
            print("room", room)

            if room.title_name:
                room.title_name = f"Chat+{self.room_name}"
            if room.message:
                current_messages = json.loads(room.message)
                current_messages.append(text_data_store)
                room.message = json.dumps(current_messages)
            else:
                room.message = json.dumps([text_data_store])

            await sync_to_async(lambda: room.save())()


            if response:
                print("response", response, data)
                self.message_processing(data, response)

            await self.channel_layer.group_send(
                self.room_name,
                {
                    "type": "chat.message",
                    "text": response,
                },
            )


    async def disconnect(self, _):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)
        pass


    async def message_processing(self, data, response):
        try:
            print("data", data)
            event_type = data.get('event_type')
            print("event_type", event_type)
            if event_type == 'chat':
                await self.get_chat_response_data(response)

            elif event_type == 'history':
                await self.handle_message_history_data()

        except Exception as e:
            print(f"Enter valid data : {str(e)}")
            await self.send(text_data=json.dumps({"message": "Enter valid data"}))


    async def get_chat_response_data(self,response):

        await self.channel_layer.group_send(
                self.room_name,
                {
                    "type": "chat.message",
                    "text": response,
                },
            )
    async def chat_message(self, event):

        await self.send(text_data=json.dumps({
            "message": event["text"]
        }))

    async def handle_message_history_data(self):
        print("chat history event working")
        try:
            room = await sync_to_async(RoomManagement.objects.get)(room_id=self.room_name)

            if room.message:
                print("room getting here")
                message_history = json.loads(room.message)

                await self.send(text_data=json.dumps({
                    "type": "message_history",
                    "history": message_history
                }))
            else:
                await self.send(text_data=json.dumps({
                    "type": "message_history",
                    "history": []
                }))
        except RoomManagement.DoesNotExist:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "No chat history found"
            }))
        except Exception as e:
            print(f"Error retrieving message history: {str(e)}")
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Failed to retrieve chat history"
            }))

    async def message_history(self, event):

        await self.send(text_data=json.dumps({
            "message": event["history"]
        }))
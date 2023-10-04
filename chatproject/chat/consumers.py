from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import Message
from django.contrib.auth.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def fetch_message(self, data):
        messages = await Message.last_10_messages()
        content = {
            'message': self.messages_json(messages)
        }
        await self.send_message(content)

    async def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(await self.message_to_json(message))
        return result

    async def message_to_json(self, message):
        return {
            'author': message.author.username,
            'content': message.content,
            'time': message.time_stamp
        }

    async def new_message(self, data):
        author = data['from']
        author_user = await User.objects.filter(username=author).first()
        message = await Message.objects.create(author=author_user, content=data['message'])
        content = {
            'command': 'new_message',
            'message': await self.message_to_json(message)
        }
        await self.chat_message(content)

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.command[data['command']](self, data)

    async def send_chat_message(self, message):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def send_message(self, message):
        await self.send(json.dumps(message))

    async def chat_message(self, event):
        message = event['message']
        await self.send(json.dumps(message))

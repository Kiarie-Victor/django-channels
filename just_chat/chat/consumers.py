from django.contrib.auth import get_user_model
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import Message
from django.utils.timesince import timesince

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):

    async def fetch_messages(self, data):
        messages = await self.get_last_10_messages()
        content = {
            'command': 'messages',
            'messages': await self.messages_to_json(messages)
        }
        await self.send_message(content)

    async def new_message(self, data):
        author_user = await self.get_user(data['from'])
        message = await self.create_message(author_user, data['message'])
        content = {
            'command': 'new_message',
            'message': await self.message_to_json(message)
        }
        await self.send_chat_message(content)

    async def get_last_10_messages(self):
        return await Message.last_10_messages()

    async def get_user(self, username):
        return await User.objects.get(username=username)

    async def create_message(self, author, content):
        return await Message.objects.create(author=author, content=content)

    async def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(await self.message_to_json(message))
        return result

    async def message_to_json(self, message):
        return {
            'author': message.author.username,
            'content': message.content,
            'timestamp': timesince(message.timestamp)
        }

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
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
    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message
    }

    async def receive(self, text_data):
        data = json.loads(text_data)
        command = data.get('command', None)
        if command is not None:
            await self.commands[command](self, data)

    async def send_chat_message(self, message):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def send_message(self, message):
        await self.send(text_data=json.dumps(message))

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))

    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message
    }

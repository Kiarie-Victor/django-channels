from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async
from .templatetags.chatextras import initials
from django.utils.timesince import timesince
from .models import Room, Message
from account.models import User
from channels.middleware import BaseMiddleware

class WebSocketAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        scope['user'] = await self.get_user(scope)
        return await super().__call__(scope, receive, send)

    @sync_to_async
    def get_user(self, scope):
        if 'user' in scope:
            return scope['user']
        return None

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' %self.room_name
        self.user = self.scope['user']
        # adding the room to the groups 
        await self.get_room()
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # inform user
        if self.user.is_staff:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type':'users_update'
                }
            )

    async def disconnect(self, text_content):
        # remove the room
        await  self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        if not self.user.is_staff:
            await self.set_room_closed()

    async def receive(self, text_data):
        text_data = json.loads(text_data)
        type = text_data['type']
        message = text_data['message']
        name = text_data['name']
        agent = text_data.get('agent', '')


        if type == 'message':
            new_message = await self.create_message(name,message,agent)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type':'chat_message',
                    'message':message,
                    'name':name,
                    'agent':agent,
                    'initials': initials(name),
                    'created_at': timesince(new_message.created_at),
                }
            )

        elif type == 'update':
            # send update to the room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type':'writing_active',
                    'message':message,
                    'name':name,
                    'agent':agent,
                    'initials': initials(name),
                }
            )

    async def writing_active( self, event):
        await self.send(text_data=json.dumps({
            'type': event['type'],
            'message': event['message'],
            'name': event['name'],
            'agent': event['agent'],
            'initials': event['initials']
        }))
    
    async def chat_message(self, event):
        message = event['message']
        name = event['name']
        agent = event['agent']
        created_at = event['created_at']
        await self.send(text_data=json.dumps({
            'type': event['type'],
            'message': message,
            'name': name,
            'agent': agent,
            'initials': event['initials'],
            'created_at': created_at,
            
        }))

    async def users_update(self, event):
        # send infor to the websocket
        await self.send(text_data=json.dumps(
            {
                'type':'users_update'
            }
        ))

    @sync_to_async
    def get_room(self):
        self.room = Room.objects.get(uuid= self.room_name)
        


    @sync_to_async
    def create_message(self, sent_by,message,agent):
        message = Message.objects.create(body=message, sent_by=sent_by)

        if agent:
            message.created_by = User.objects.get(pk=agent)
            message.save()
            self.room.messages.add(message)
        else:
            self.room.messages.add(message)
            message.save()
        return message

    @sync_to_async
    def set_room_closed(self):
        self.room.status = Room.CLOSED
        self.room.save()
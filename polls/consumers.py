import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db import IntegrityError

from .models import Poll, Choice, UserPollHistory


class PollConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.poll_id = self.scope['url_route']['kwargs']['poll_id']
        self.user = self.scope['user']
        self.room_group_name = f'poll_{self.poll_id}'

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
        choice_id = data['choice_id']

        response = await database_sync_to_async(self.process_vote)(choice_id)

        if "error" in response.keys():
            await self.send(json.dumps(response))
        else:
            await self.channel_layer.group_send(
                self.room_group_name,
                response
            )

    async def choice_update(self, event):
        choice_id = event['choice_id']
        votes = event['votes']
        choice_text = event['choice_text']

        # Send the updated choice data to WebSocket
        await self.send(text_data=json.dumps({
            'choice_id': choice_id,
            'choice_text': choice_text,
            'votes': votes
        }))

    def process_vote(self, choice_id):
        try:
            poll = Poll.objects.get(pk=self.poll_id)
            choice = Choice.objects.get(pk=choice_id, poll=poll)

            try:
                UserPollHistory.objects.create(user=self.user, poll=poll, choice=choice)
            except IntegrityError:
                return {"error": "You have already voted!"}

            choice.votes += 1
            choice.save()

            return {
                    'type': 'choice_update',
                    'choice_id': choice.id,
                    'choice_text': choice.choice_text,
                    'votes': choice.votes
            }

        except (Poll.DoesNotExist, Choice.DoesNotExist):
            return {"error": "Not found!"}

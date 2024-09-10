import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db import IntegrityError

from .models import Poll, Choice, UserPollHistory


class VoteConsumer(AsyncWebsocketConsumer):
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
        action = data['action']

        response = await database_sync_to_async(self.process_vote)(choice_id, action == "vote")

        if "error" in response.keys():
            await self.send(json.dumps(response))
        else:
            await self.channel_layer.group_send(
                self.room_group_name,
                response
            )

    async def choice_update(self, event):
        choice_id = event['choice_id']
        vote_count = event['vote_count']
        choice_text = event['choice_text']
        up_voted = event['up_voted']

        # Send the updated choice data to WebSocket
        await self.send(text_data=json.dumps({
            'up_voted': up_voted,
            'choice_id': choice_id,
            'choice_text': choice_text,
            'votes': vote_count
        }))

    def process_vote(self, choice_id, up_voted):
        try:
            poll = Poll.objects.get(pk=self.poll_id)
            user_choice = None

            if up_voted:
                try:
                    choice = Choice.objects.get(pk=choice_id, poll=poll)
                    UserPollHistory.objects.create(user=self.user, poll=poll, choice=choice)
                    choice.vote_count += 1
                    choice.save()
                    user_choice = choice
                except Choice.DoesNotExist:
                    return {"error": "Invalid choice!"}
                except IntegrityError:
                    return {"error": "You have already voted!"}
            else:
                try:
                    poll_history = UserPollHistory.objects.get(user=self.user, poll=poll)
                    poll_history.choice.vote_count -= 1
                    poll_history.choice.save()
                    user_choice = poll_history.choice
                    poll_history.delete()
                except UserPollHistory.DoesNotExist:
                    return {"error": "You have not voted yet!"}

            return {
                    'type': 'choice_update',
                    'user': self.user.username,
                    'up_voted': up_voted,
                    'choice_id': user_choice.id,
                    'choice_text': user_choice.choice_text,
                    'vote_count': user_choice.vote_count
            }

        except Poll.DoesNotExist:
            return {"error": "Poll Not found!"}


class PollResultsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.poll_id = self.scope['url_route']['kwargs']['poll_id']
        self.room_group_name = f'poll_{self.poll_id}'

        self.user = self.scope['user']

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
        pass

    async def choice_update(self, event):
        choice_id = event['choice_id']
        vote_count = event['vote_count']
        choice_text = event['choice_text']
        voter = event['user']
        up_voted = event['up_voted']

        top_choice = await database_sync_to_async(self.get_top_choice)(self.poll_id)

        await self.send(text_data=json.dumps({
            'poll_id': self.poll_id,
            'voted': self.user.username == voter,
            'up_voted': up_voted,
            'choice_id': choice_id,
            'choice_text': choice_text,
            'votes': vote_count,
            'top_choice': top_choice
        }))

    def get_top_choice(self, poll_id):
        poll = Poll.objects.get(pk=poll_id)
        choices = poll.choices.all()
        top_choice = choices.order_by('-vote_count')[0]

        return top_choice.choice_text


class NewPollConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'poll_results'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def new_poll(self, event):
        poll_data = event['poll_data']
        poll_data.update({"voted": False})
        await self.send(text_data=json.dumps(poll_data))

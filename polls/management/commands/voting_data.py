from django.core.management.base import BaseCommand
from django.utils import timezone

from polls.models import User, UserPollHistory, Poll, Choice


class Command(BaseCommand):
    help = "Enters users' votes"

    def handle(self, *args, **options):
        admin_user = User.objects.get(username='junaid_khan')
        regular_user = User.objects.get(username='ahmad_khan')

        # Tuple for (Poll title, choice text) that admin user has voted
        admin_votes = [
            ('Impact of Blockchain', 'Voting Systems'),
            ('Favorite Travel Destinations', 'Edinburgh')
        ]

        # Tuple for (Poll title, choice text) that regular user has voted
        regular_votes = [
            ('Impact of Blockchain', 'Financial Services'),
            ('Top Sports Events', 'Olympics'),
            ('Important Health Topics', 'Nutrition and Diet'),
            ('Critical Education Reforms', 'Student Assessment Methods')
        ]

        # Admin user votes
        for poll_title, choice_text in admin_votes:
            poll = Poll.objects.get(title=poll_title)
            choice = Choice.objects.get(poll=poll, choice_text=choice_text)
            UserPollHistory.objects.create(
                user=admin_user,
                poll=poll,
                choice=choice,
                voting_time=timezone.now()
            )

        # Regular user votes
        for poll_title, choice_text in regular_votes:
            poll = Poll.objects.get(title=poll_title)
            choice = Choice.objects.get(poll=poll, choice_text=choice_text)
            UserPollHistory.objects.create(
                user=regular_user,
                poll=poll,
                choice=choice,
                voting_time=timezone.now()
            )

        self.stdout.write(self.style.SUCCESS('Successfully added votes for users'))

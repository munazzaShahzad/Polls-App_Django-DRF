import datetime

from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from polls.models import User, Poll, Choice, UserPollHistory, UserTagHistory, Tag, Category


class UserPollHistoryTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='temp user', password='12345678', email='user@example2.com')
        self.user.user_type = 2
        self.user.save()
        self.user.refresh_from_db()
        self.poll = Poll.objects.create(title='Test Title', question='Test Question?',
                                        expiry_date=timezone.now() + datetime.timedelta(days=2),
                                        category=Category.objects.create(name='category 1'),
                                        created_by=self.user)
        tag1 = Tag.objects.create(name='tag 1')
        tag2 = Tag.objects.create(name='tag 2')
        self.poll.tags.add(tag1)
        self.poll.tags.add(tag2)
        self.choice = Choice.objects.create(poll=self.poll, choice_text='Red')

    def test_voting_time_cannot_be_future(self):
        future_date = timezone.now() + timezone.timedelta(days=1)
        with self.assertRaises(ValidationError):
            history = UserPollHistory.objects.create(
                user=self.user,
                poll=self.poll,
                choice=self.choice,
                voting_time=future_date
            )
            history.full_clean()

    def test_unique_together_constraint(self):
        UserPollHistory.objects.create(
            user=self.user,
            poll=self.poll,
            choice=self.choice
        )
        with self.assertRaises(IntegrityError):
            UserPollHistory.objects.create(
                user=self.user,
                poll=self.poll,
                choice=self.choice
            )


class UserTagHistoryTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='temp user', password='12345678', email='user@example2.com')
        self.user.user_type = 2
        self.user.save()
        self.user.refresh_from_db()
        self.poll = Poll.objects.create(title='Test Title', question='Test Question?',
                                        expiry_date=timezone.now() + datetime.timedelta(days=2),
                                        category=Category.objects.create(name='category 1'),
                                        created_by=self.user)
        self.tag = Tag.objects.create(name='Color')
        self.poll.tags.add(self.tag)

    def test_update_tag_history_signal_single_vote(self):
        choice = Choice.objects.create(poll=self.poll, choice_text='Red')
        UserPollHistory.objects.create(user=self.user, poll=self.poll, choice=choice)
        user_tag_history = UserTagHistory.objects.get(user=self.user)
        self.assertIn(str(self.tag.id), user_tag_history.tag_history)
        self.assertEqual(user_tag_history.tag_history[str(self.tag.id)], 1)

import datetime

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TransactionTestCase
from django.utils import timezone

from polls.models import Poll, Choice, Category, Tag, User


class PollModelTestCase(TransactionTestCase):

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

    def tearDown(self):
        self.poll = None
        Poll.objects.filter(title='Test Title').delete()
        Category.objects.all().delete()

    def test_created_poll(self):
        self.assertEqual(self.poll.title, 'Test Title')
        self.assertEqual(self.poll.category.name, 'category 1')
        self.assertEqual(self.poll.created_by.username, self.user.username)
        self.assertEqual(self.poll.tags.count(), 2)

    def test_create_choice(self):
        Choice.objects.create(poll=self.poll, choice_text='sample choice 1')
        Choice.objects.create(poll=self.poll, choice_text='sample choice 2')
        self.assertEqual(self.poll.choices.count(), 2)

    def test_poll_expiry_date_validation(self):
        with self.assertRaises(ValidationError):
            poll = Poll.objects.create(
                title='Invalid Poll',
                question='This should fail',
                expiry_date=timezone.now(),
                category=self.poll.category,
                created_by=self.user
            )
            poll.full_clean()

    def test_non_admin_user_cannot_create_poll(self):
        regular_user = User.objects.create_user(username='regular_user', password='12345678',
                                                email='regular@example.com',
                                                user_type=1)
        with self.assertRaises(ValidationError):
            poll = Poll.objects.create(
                title='Should Not Be Created',
                question='This poll should not be allowed',
                expiry_date=timezone.now() + datetime.timedelta(days=2),
                category=self.poll.category,
                created_by=regular_user
            )
            poll.full_clean()

    def test_choice_text_min_length_validation(self):
        with self.assertRaises(ValidationError):
            choice = Choice.objects.create(poll=self.poll, choice_text='A')
            choice.full_clean()

    def test_poll_str_method(self):
        self.assertEqual(str(self.poll), f"{self.poll.id}: {self.poll.title}")

    def test_poll_deletion_cascade(self):
        Choice.objects.create(poll=self.poll, choice_text='sample choice 1')
        Choice.objects.create(poll=self.poll, choice_text='sample choice 2')
        self.poll.delete()
        self.assertEqual(Choice.objects.filter(poll=self.poll).count(), 0)

    def test_poll_tag_association(self):
        tag1 = Tag.objects.get(name='tag 1')
        self.assertEqual(self.poll.tags.count(), 2)
        self.poll.tags.remove(tag1)
        self.assertEqual(self.poll.tags.count(), 1)

    def test_duplicate_choices(self):
        Choice.objects.create(poll=self.poll, choice_text='sample choice 1')
        with self.assertRaises(IntegrityError):
            Choice.objects.create(poll=self.poll, choice_text='sample choice 1')

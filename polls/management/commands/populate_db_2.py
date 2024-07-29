from django.core.management.base import BaseCommand

from polls.models import Category, Tag, User, Poll, Choice


class Command(BaseCommand):

    def create_objects(self, model, objects):
        model.objects.bulk_create(objects)

    def update_objects(self, model, objects, fields):
        model.objects.bulk_update(objects, fields)

    def handle(self, *args, **kwargs):
        # Category objects
        categories = [
            Category(name='Business'),
            Category(name='Travel'),
            Category(name='Sports'),
            Category(name='Entertainment')
        ]

        self.create_objects(Category, categories)

        # Tag objects
        tags = [
            Tag(name='Blockchain'),
            Tag(name='Virtual Reality'),
            Tag(name='Startups'),
            Tag(name='Physical Activity')
        ]

        self.create_objects(Tag, tags)

        # Admin Users
        admin_users = [
             User(username='junaid_khan', password='123_Junaid', first_name='Junaid',
                  last_name='Khan', user_type=2)
        ]

        self.create_objects(User, admin_users)

        # Get specific categories and tags needed for the polls
        business_category = Category.objects.get(name='Business')
        travel_category = Category.objects.get(name='Travel')
        sports_category = Category.objects.get(name='Sports')
        entertainment_category = Category.objects.get(name='Entertainment')

        blockchain_tag = Tag.objects.get(name='Blockchain')
        vr_tag = Tag.objects.get(name='Virtual Reality')
        startup_tag = Tag.objects.get(name='Startups')
        ai_tag = Tag.objects.get(name='Artificial Intelligence')
        mental_health_tag = Tag.objects.get(name='Mental Health')
        physical_activity_tag = Tag.objects.get(name='Physical Activity')

        admin_user = User.objects.get(first_name='Junaid', last_name='Khan')

        # Poll objects
        polls = [
            Poll(title='Blockchain',
                 question='How do you think blockchain technology will impact businesses?',
                 expiry_date='2024-08-10 23:59:59', category=business_category,
                 created_by=admin_user),
            Poll(title='Favorite Travel Destinations',
                 question='What are your top travel destinations for 2025?',
                 expiry_date='2024-08-20 23:59:59', category=travel_category,
                 created_by=admin_user),
            Poll(title='Top Sports Events',
                 question='Which sports event are you most excited about this year?',
                 expiry_date='2024-09-15 23:59:59', category=sports_category,
                 created_by=admin_user),
            Poll(title='Virtual Reality in Entertainment',
                 question='How is virtual reality changing the entertainment industry?',
                 expiry_date='2024-10-31 23:59:59', category=entertainment_category,
                 created_by=admin_user)
        ]

        self.create_objects(Poll, polls)

        poll_1 = Poll.objects.get(title='Blockchain')
        poll_2 = Poll.objects.get(title='Favorite Travel Destinations')
        poll_3 = Poll.objects.get(title='Top Sports Events')
        poll_4 = Poll.objects.get(title='Virtual Reality in Entertainment')

        # Create Choices for the polls
        choices = [
            # Choices for poll1
            Choice(poll=poll_1, choice_text='Financial Services'),
            Choice(poll=poll_1, choice_text='Supply Chain Management'),
            Choice(poll=poll_1, choice_text='Healthcare'),
            Choice(poll=poll_1, choice_text='Real Estate'),
            Choice(poll=poll_1, choice_text='Voting Systems'),
            # Choices for poll2
            Choice(poll=poll_2, choice_text='Paris'),
            Choice(poll=poll_2, choice_text='Tokyo'),
            Choice(poll=poll_2, choice_text='New York'),
            Choice(poll=poll_2, choice_text='Edinburgh'),
            Choice(poll=poll_2, choice_text='Kashmir'),
            # Choices for poll3
            Choice(poll=poll_3, choice_text='Olympics'),
            Choice(poll=poll_3, choice_text='Fifa World Cup'),
            Choice(poll=poll_3, choice_text='Champions Trophy'),
            Choice(poll=poll_3, choice_text='Wimbledon'),
            # Choices for poll4
            Choice(poll=poll_4, choice_text='Gaming'),
            Choice(poll=poll_4, choice_text='Movies'),
            Choice(poll=poll_4, choice_text='Virtual Tours')
        ]

        self.create_objects(Choice, choices)

        # Add Tags to Polls
        poll_1.tags.add(blockchain_tag, startup_tag)
        poll_2.tags.add(physical_activity_tag, mental_health_tag)
        poll_3.tags.add(mental_health_tag)
        poll_4.tags.add(vr_tag, ai_tag)

        # Update Poll title field
        poll_1.title = 'Impact of Blockchain'

        self.update_objects(Poll, [poll_1], ['title'])

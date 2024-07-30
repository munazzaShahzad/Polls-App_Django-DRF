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
            Category(name='Technology'),
            Category(name='Science'),
            Category(name='Health'),
            Category(name='Environment'),
            Category(name='Education'),
            Category(name='Politics'),
            Category(name='Economics')
        ]

        self.create_objects(Category, categories)

        # Tag objects
        tags = [
            Tag(name='Artificial Intelligence'),
            Tag(name='Climate Change'),
            Tag(name='Public Health'),
            Tag(name='Renewable Energy'),
            Tag(name='Space Exploration'),
            Tag(name='Machine Learning'),
            Tag(name='Biotechnology'),
            Tag(name='Education Reform'),
            Tag(name='Cybersecurity'),
            Tag(name='Mental Health'),
            Tag(name='Global Warming'),
            Tag(name='Scientific Research'),
            Tag(name='Policy Making'),
            Tag(name='Economic Growth'),
            Tag(name='Data Privacy')
        ]

        self.create_objects(Tag, tags)

        # Admin Users
        admin_users = [
            User(username='usman_tariq', password='123_Usman', first_name='Usman',
                 last_name='Tariq', user_type=2),
            User(username='bilal_rahman', password='123_Bilal', first_name='Bilal',
                 last_name='Rahman', user_type=2)
        ]

        self.create_objects(User, admin_users)

        # Regular Users
        regular_users = [
            User(username='ahmad_khan', password='Ahmad_123', first_name='Ahmad',
                 last_name='Khan', user_type=1),
            User(username='faisal_malik', password='Faisal_123', first_name='Faisal',
                 last_name='Malik', user_type=1),
            User(username='ayesha_riaz', password='Ayesha_123', first_name='Ayesha',
                 last_name='Riaz', user_type=1),
            User(username='imran_ali', password='Imran_123', first_name='Imran',
                 last_name='Ali', user_type=1),
            User(username='hina_malik', password='Hina_123', first_name='Hina',
                 last_name='Malik', user_type=1),
            User(username='tariq_javed', password='Tariq_123', first_name='Tariq',
                 last_name='Javed', user_type=1),
            User(username='zainab_farooq', password='Zainab_123', first_name='Zainab',
                 last_name='Farooq', user_type=1),
            User(username='shahid_usman', password='Shahid_123', first_name='Shahid',
                 last_name='Usman', user_type=1)
        ]

        self.create_objects(User, regular_users)

        # Get specific categories and tags needed for the polls
        technology_category = Category.objects.get(name='Technology')
        environment_category = Category.objects.get(name='Environment')
        health_category = Category.objects.get(name='Health')
        education_category = Category.objects.get(name='Education')

        ai_tag = Tag.objects.get(name='Artificial Intelligence')
        ml_tag = Tag.objects.get(name='Machine Learning')
        climate_change_tag = Tag.objects.get(name='Climate Change')
        renewable_energy_tag = Tag.objects.get(name='Renewable Energy')
        public_health_tag = Tag.objects.get(name='Public Health')
        mental_health_tag = Tag.objects.get(name='Mental Health')
        education_reform_tag = Tag.objects.get(name='Education Reform')
        scientific_research_tag = Tag.objects.get(name='Scientific Research')

        admin_users = [User.objects.get(username='usman_tariq'), User.objects.get(username='bilal_rahman')]

        # Poll objects
        polls = [
            Poll(title='Best Advancements in AI',
                 question='What is the most significant advancement in artificial intelligence?',
                 expiry_date='2024-07-31 23:59:59', category=technology_category,
                 created_by=admin_users[0]),
            Poll(title='Top Environmental Issues',
                 question='What do you think is the most pressing environmental issue today?',
                 expiry_date='2024-08-03 23:59:59', category=environment_category,
                 created_by=admin_users[0]),
            Poll(title='Important Health Topics',
                 question='Which health topic do you think should receive more attention?',
                 expiry_date='2024-09-20 23:59:59', category=health_category,
                 created_by=admin_users[1]),
            Poll(title='Critical Education Reforms',
                 question='What are the most critical areas for education reform?',
                 expiry_date='2024-11-30 23:59:59', category=education_category,
                 created_by=admin_users[1])
        ]

        self.create_objects(Poll, polls)

        polls = [
            Poll.objects.get(title='Best Advancements in AI'),
            Poll.objects.get(title='Top Environmental Issues'),
            Poll.objects.get(title='Important Health Topics'),
            Poll.objects.get(title='Critical Education Reforms')
        ]

        # Create Choices for the polls
        choices = [
            # Choices for poll1
            Choice(poll=polls[0], choice_text='Deep Learning'),
            Choice(poll=polls[0], choice_text='Natural Language Processing'),
            Choice(poll=polls[0], choice_text='Computer Vision'),
            Choice(poll=polls[0], choice_text='Reinforcement Learning'),
            Choice(poll=polls[0], choice_text='Robotics'),
            # Choices for poll2
            Choice(poll=polls[1], choice_text='Climate Change'),
            Choice(poll=polls[1], choice_text='Deforestation'),
            Choice(poll=polls[1], choice_text='Pollution'),
            Choice(poll=polls[1], choice_text='Ocean Acidification'),
            Choice(poll=polls[1], choice_text='Biodiversity Loss'),
            # Choices for poll3
            Choice(poll=polls[2], choice_text='Mental Health Awareness'),
            Choice(poll=polls[2], choice_text='Chronic Disease Management'),
            Choice(poll=polls[2], choice_text='Health Care Accessibility'),
            Choice(poll=polls[2], choice_text='Nutrition and Diet'),
            # Choices for poll4
            Choice(poll=polls[3], choice_text='Curriculum Updates'),
            Choice(poll=polls[3], choice_text='Teacher Training'),
            Choice(poll=polls[3], choice_text='Student Assessment Methods'),
            Choice(poll=polls[3], choice_text='Access to Technology')
        ]

        self.create_objects(Choice, choices)

        # Add Tags to Polls
        polls[0].tags.add(ai_tag, ml_tag)
        polls[1].tags.add(climate_change_tag, renewable_energy_tag)
        polls[2].tags.add(public_health_tag, mental_health_tag)
        polls[3].tags.add(education_reform_tag, scientific_research_tag)

        # Update Polls created_by field
        polls[1].created_by = admin_users[1]
        polls[2].created_by = admin_users[0]

        self.update_objects(Poll, [polls[1], polls[2]], ['created_by'])

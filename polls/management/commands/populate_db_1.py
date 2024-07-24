from django.core.management.base import BaseCommand

from polls.models import Category, Tag, User, Poll, Choice


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        # Category objects
        Category.objects.create(name='Technology')
        Category.objects.create(name='Science')
        Category.objects.create(name='Health')
        Category.objects.create(name='Environment')
        Category.objects.create(name='Education')
        Category.objects.create(name='Politics')
        Category.objects.create(name='Economics')

        # Tag objects
        Tag.objects.create(name='Artificial Intelligence')
        Tag.objects.create(name='Climate Change')
        Tag.objects.create(name='Public Health')
        Tag.objects.create(name='Renewable Energy')
        Tag.objects.create(name='Space Exploration')
        Tag.objects.create(name='Machine Learning')
        Tag.objects.create(name='Biotechnology')
        Tag.objects.create(name='Education Reform')
        Tag.objects.create(name='Cybersecurity')
        Tag.objects.create(name='Mental Health')
        Tag.objects.create(name='Global Warming')
        Tag.objects.create(name='Scientific Research')
        Tag.objects.create(name='Policy Making')
        Tag.objects.create(name='Economic Growth')
        Tag.objects.create(name='Data Privacy')

        # Create dictionaries for Categories and Tags for using in the following commands
        categories = {
            'Technology': Category.objects.get(name='Technology'),
            'Science': Category.objects.get(name='Science'),
            'Health': Category.objects.get(name='Health'),
            'Environment': Category.objects.get(name='Environment'),
            'Education': Category.objects.get(name='Education'),
            'Politics': Category.objects.get(name='Politics'),
            'Economics': Category.objects.get(name='Economics')
        }

        tags = {
            'Artificial Intelligence': Tag.objects.get(name='Artificial Intelligence'),
            'Climate Change': Tag.objects.get(name='Climate Change'),
            'Public Health': Tag.objects.get(name='Public Health'),
            'Renewable Energy': Tag.objects.get(name='Renewable Energy'),
            'Space Exploration': Tag.objects.get(name='Space Exploration'),
            'Machine Learning': Tag.objects.get(name='Machine Learning'),
            'Biotechnology': Tag.objects.get(name='Biotechnology'),
            'Education Reform': Tag.objects.get(name='Education Reform'),
            'Cybersecurity': Tag.objects.get(name='Cybersecurity'),
            'Mental Health': Tag.objects.get(name='Mental Health'),
            'Global Warming': Tag.objects.get(name='Global Warming'),
            'Scientific Research': Tag.objects.get(name='Scientific Research'),
            'Policy Making': Tag.objects.get(name='Policy Making'),
            'Economic Growth': Tag.objects.get(name='Economic Growth'),
            'Data Privacy': Tag.objects.get(name='Data Privacy')
        }

        # Admin Users
        admin1 = User.objects.create(username='usman_tariq', password='123_Usman', first_name='Usman',
                                     last_name='Tariq', user_type=2)
        admin2 = User.objects.create(username='bilal_rahman', password='123_Bilal', first_name='Bilal',
                                     last_name='Rahman', user_type=2)

        # Regular Users
        User.objects.create(username='ahmad_khan', password='Ahmad_123', first_name='Ahmad',
                            last_name='Khan', user_type=1)
        User.objects.create(username='faisal_malik', password='Faisal_123', first_name='Faisal',
                            last_name='Malik', user_type=1)
        User.objects.create(username='ayesha_riaz', password='Ayesha_123', first_name='Ayesha',
                            last_name='Riaz', user_type=1)
        User.objects.create(username='imran_ali', password='Imran_123', first_name='Imran',
                            last_name='Ali', user_type=1)
        User.objects.create(username='hina_malik', password='Hina_123', first_name='Hina',
                            last_name='Malik', user_type=1)
        User.objects.create(username='tariq_javed', password='Tariq_123', first_name='Tariq',
                            last_name='Javed', user_type=1)
        User.objects.create(username='zainab_farooq', password='Zainab_123', first_name='Zainab',
                            last_name='Farooq', user_type=1)
        User.objects.create(username='shahid_usman', password='Shahid_123', first_name='Shahid',
                            last_name='Usman', user_type=1)

        # Poll objects
        poll1 = Poll.objects.create(title='Best Advancements in AI',
                                    question='What is the most significant advancement in artificial intelligence?',
                                    expiry_date='2024-07-31 23:59:59', category=categories['Technology'],
                                    created_by=admin1)
        poll2 = Poll.objects.create(title='Top Environmental Issues',
                                    question='What do you think is the most pressing environmental issue today?',
                                    expiry_date='2024-08-03 23:59:59', category=categories['Environment'],
                                    created_by=admin1)
        poll3 = Poll.objects.create(title='Important Health Topics',
                                    question='Which health topic do you think should receive more attention?',
                                    expiry_date='2024-09-20 23:59:59', category=categories['Health'],
                                    created_by=admin2)
        poll4 = Poll.objects.create(title='Critical Education Reforms',
                                    question='What are the most critical areas for education reform?',
                                    expiry_date='2024-11-30 23:59:59', category=categories['Education'],
                                    created_by=admin2)

        # create Choices for polls
        Choice.objects.create(poll=poll1, choice_text='Deep Learning')
        Choice.objects.create(poll=poll1, choice_text='Natural Language Processing')
        Choice.objects.create(poll=poll1, choice_text='Computer Vision')
        Choice.objects.create(poll=poll1, choice_text='Reinforcement Learning')
        Choice.objects.create(poll=poll1, choice_text='Robotics')

        Choice.objects.create(poll=poll2, choice_text='Climate Change')
        Choice.objects.create(poll=poll2, choice_text='Deforestation')
        Choice.objects.create(poll=poll2, choice_text='Pollution')
        Choice.objects.create(poll=poll2, choice_text='Ocean Acidification')
        Choice.objects.create(poll=poll2, choice_text='Biodiversity Loss')

        Choice.objects.create(poll=poll3, choice_text='Mental Health Awareness')
        Choice.objects.create(poll=poll3, choice_text='Chronic Disease Management')
        Choice.objects.create(poll=poll3, choice_text='Health Care Accessibility')
        Choice.objects.create(poll=poll3, choice_text='Nutrition and Diet')

        Choice.objects.create(poll=poll4, choice_text='Curriculum Updates')
        Choice.objects.create(poll=poll4, choice_text='Teacher Training')
        Choice.objects.create(poll=poll4, choice_text='Student Assessment Methods')
        Choice.objects.create(poll=poll4, choice_text='Access to Technology')

        # Add Tags to Polls
        poll1.tags.add(tags['Artificial Intelligence'], tags['Machine Learning'])
        poll2.tags.add(tags['Climate Change'], tags['Renewable Energy'])
        poll3.tags.add(tags['Public Health'], tags['Mental Health'])
        poll4.tags.add(tags['Education Reform'], tags['Scientific Research'])

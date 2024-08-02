from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from polls.models import User, UserProfile


class Command(BaseCommand):
    help = 'Assigns email addresses to all users and ensures user profiles are created'

    def handle(self, *args, **options):
        # List of email patterns
        email_patterns = {
            'usman_tariq': 'usman_tariq@gmail.com',
            'bilal_rahman': 'bilal_rahman@gmail.com',
            'ahmad_khan': 'ahmad_khan@gmail.com',
            'faisal_malik': 'faisal_malik@gmail.com',
            'ayesha_riaz': 'ayesha_riaz@gmail.com',
            'imran_ali': 'imran_ali@gmail.com',
            'hina_malik': 'hina_malik@gmail.com',
            'tariq_javed': 'tariq_javed@gmail.com',
            'zainab_farooq': 'zainab_farooq@gmail.com',
            'shahid_usman': 'shahid_usman@gmail.com',
            'junaid_khan': 'junaid_khan@gmail.com'
        }

        for username, email in email_patterns.items():
            try:
                user = User.objects.get(username=username)
                user.email = email
                user.save()  # This will trigger the post_save signal

            except ObjectDoesNotExist:
                self.stdout.write(self.style.ERROR(f'User with username {username} does not exist'))

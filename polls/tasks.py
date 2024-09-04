import datetime

from celery import shared_task
from django.core.mail import send_mail
from django.core.mail import BadHeaderError
from smtplib import SMTPSenderRefused
from django.utils import timezone

from django_site import settings


@shared_task
def send_password_reset_email(to_email, reset_url):
    try:
        send_mail(
            subject="Password Reset Request",
            message=f"Click the link to reset your password: {reset_url}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[to_email],
            fail_silently=False,
        )
    except SMTPSenderRefused as e:
        print(f"SMTP error: {e}")
    except BadHeaderError:
        print("Invalid header found.")
    except Exception as e:
        print(f"Unexpected error: {e}")


@shared_task
def send_poll_results_email():
    from polls.models import User, Poll, UserPollHistory

    day = timezone.now().date()
    start_of_day = timezone.make_aware(timezone.datetime.combine(day, timezone.datetime.min.time()))
    end_of_day = timezone.make_aware(timezone.datetime.combine(day, timezone.datetime.max.time()))

    # users to email
    users = User.objects.all()

    for user in users:
        # Get polls where the user has voted today
        voted_polls = UserPollHistory.objects.filter(
            user=user,
            voting_time__range=(start_of_day, end_of_day)
        ).values_list('poll_id', flat=True).distinct()

        polls = Poll.objects.filter(id__in=voted_polls, expiry_date__gte=start_of_day).prefetch_related('choices')

        email_body = ""

        for poll in polls:
            email_body += "Here are some updates of the poll(s) you voted on recently:\n\n"
            choices = poll.choices.all()
            top_choice = choices.order_by('-vote_count')[0]

            if top_choice:
                email_body += (
                        f"Poll: {poll.title}\n"
                        f"Question: {poll.question}\n"
                        f"Top Choice: {top_choice.choice_text} with {top_choice.vote_count} votes\n"
                        f"Choices:\n"
                        + "".join([f"\t{choice.choice_text}\n" for choice in choices])
                        + "\n\n"
                )

        if email_body.strip():
            send_mail(
                subject="See the Latest Results from Your Poll Votes!",
                message=email_body,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )

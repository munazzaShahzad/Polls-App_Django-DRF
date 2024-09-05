from celery import shared_task
from django.core.mail import send_mail
from django.core.mail import BadHeaderError
from smtplib import SMTPSenderRefused
from django.template.loader import render_to_string
from django.utils import timezone

from django_site import settings


@shared_task
def send_password_reset_email(to_email, reset_url):
    message = render_to_string('polls/password_reset_email.html', {'reset_url': reset_url})

    try:
        send_mail(
            subject="Password Reset Request",
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[to_email],
            fail_silently=False,
            html_message=message
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

        for poll in polls:
            top_choice = poll.choices.order_by('-vote_count')[0]
            poll.top_choice = top_choice

        email_body = render_to_string('polls/poll_results_email.html', {'polls': polls})

        if polls:
            send_mail(
                subject="See the Latest Results from Your Poll Votes!",
                message=email_body,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
                html_message=email_body
            )

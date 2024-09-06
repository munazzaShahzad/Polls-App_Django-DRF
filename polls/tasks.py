import datetime

from celery import shared_task
from django.core.mail import send_mail
from django.core.mail import BadHeaderError
from smtplib import SMTPSenderRefused
from django.db.models import Q, Count
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

    end_time = timezone.now()
    start_time = end_time - timezone.timedelta(hours=24)

    # users to email
    users = User.objects.all()

    for user in users:
        # Get polls where the user has voted today
        voted_polls = UserPollHistory.objects.filter(
            user=user,
            voting_time__range=(start_time, end_time)
        ).values_list('poll_id', flat=True).distinct()

        polls = Poll.objects.filter(id__in=voted_polls, expiry_date__gte=start_time).prefetch_related('choices')

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


@shared_task
def send_welcome_email(to_email, first_name):
    message = render_to_string('polls/welcome_email.html', {'first_name': first_name})

    try:
        send_mail(
            subject="Welcome to VoteStream!",
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[to_email],
            fail_silently=False,
            html_message=message
        )
    except Exception as e:
        print(f"Unexpected error: {e}")


@shared_task
def send_recommended_polls_email():
    from polls.models import User, Poll, UserPollHistory

    def send_email(mail, poll_recommendations):
        if poll_recommendations:
            context = {
                'polls': [
                    {
                        'id': poll.id,
                        'title': poll.title,
                        'question': poll.question,
                        'expiry_date': poll.expiry_date,
                    }
                    for poll in poll_recommendations
                ],
                'base_url': "http://192.168.6.91:8000",
            }

            message = render_to_string('polls/recommended_polls_email.html', context)

            try:
                send_mail(
                    subject="Check Out These Polls Recommended for You!",
                    message=message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[mail],
                    fail_silently=False,
                    html_message=message
                )
            except Exception as e:
                print(f"Error sending email to {user.email}: {e}")

    # users with no votes in poll history
    users_with_no_history = User.objects.annotate(
        history_count=Count('userpollhistory')
    ).filter(history_count=0)

    for user in users_with_no_history:
        recommended_polls = Poll.objects.filter(
            expiry_date__gt=timezone.now() + datetime.timedelta(minutes=10)
        ).order_by('expiry_date')[:5]
        send_email(user.email, recommended_polls)

    # users with no votes in past 7 days
    one_week_ago = timezone.now() - datetime.timedelta(weeks=1)
    old_voters = (UserPollHistory.objects.filter(voting_time__lt=one_week_ago)
                  .values_list('user_id', flat=True).distinct())
    recent_voters = (UserPollHistory.objects.filter(voting_time__gt=one_week_ago)
                     .values_list('user_id', flat=True).distinct())

    users_with_no_recent_votes = User.objects.filter(
        Q(id__in=old_voters) & ~Q(id__in=recent_voters)
    ).distinct()

    for user in users_with_no_recent_votes:
        user_tag_history = user.usertaghistory.tag_history
        sorted_tags = sorted(user_tag_history.items(), key=lambda x: x[1], reverse=True)[:5]
        top_tags = [tag_id for tag_id, count in sorted_tags]

        voted_poll_ids = UserPollHistory.objects.filter(user=user).values_list('poll_id', flat=True)
        recommended_polls = Poll.objects.filter(
            Q(expiry_date__gt=timezone.now() + datetime.timedelta(minutes=10)) &
            Q(tags__in=top_tags)
        ).exclude(id__in=voted_poll_ids).distinct().order_by('expiry_date')[:5]

        send_email(user.email, recommended_polls)


@shared_task
def send_password_change_email(to_email, change_time):
    message = render_to_string('polls/password_change_email.html', {'change_time': change_time})

    try:
        send_mail(
            subject="Your Password Has Been Changed",
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[to_email],
            fail_silently=False,
            html_message=message
        )
    except Exception as e:
        print(f"Unexpected error: {e}")

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver

from .user import User
from .poll import Poll, Choice


def validate_not_future_date(value):
    if value > timezone.now():
        raise ValidationError("Voting time cannot be in the future.")


class UserPollHistory(models.Model):
    """
    Stores history of polls user has voted in, and user's choice.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    voting_time = models.DateTimeField(default=timezone.now, validators=[validate_not_future_date])

    class Meta:
        unique_together = ('user', 'poll')
        db_table = "user_poll_history"
        verbose_name_plural = "User Poll History"


class UserTagHistory(models.Model):
    """
    Stores history of tags affiliated to polls that user voted in.
    """
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    tag_history = models.JSONField(default=dict)

    class Meta:
        db_table = "user_tag_history"
        verbose_name_plural = "User Tag History"


@receiver(post_save, sender=UserPollHistory)
def update_tag_history(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        user_tag_history, _ = UserTagHistory.objects.get_or_create(user=user)

        for tag in instance.poll.tags.all():
            if str(tag.id) in user_tag_history.tag_history:
                user_tag_history.tag_history[str(tag.id)] += 1
            else:
                user_tag_history.tag_history[str(tag.id)] = 1

        user_tag_history.save()

from django.db import models
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from .user import User
from .poll import Poll, Choice


def validate_not_future_date(value):
    if value > timezone.now():
        raise ValidationError("Voting time cannot be in the future.")


class UserPollHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    voting_time = models.DateTimeField(default=timezone.now, validators=[validate_not_future_date])

    class Meta:
        unique_together = ('user', 'poll')
        db_table = "user_poll_history"


class UserTagHistory(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    tag_history = models.JSONField(default=dict)

    class Meta:
        db_table = "user_tag_history"

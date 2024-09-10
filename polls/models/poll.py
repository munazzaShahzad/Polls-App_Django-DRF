import datetime

from django.utils import timezone
from django.db import models
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError

from .category import Category
from .tag import Tag
from .user import User


def validate_expiry_date(value):
    if value <= timezone.now() + datetime.timedelta(days=1):
        raise ValidationError("Expiry date must be at least one day in the future.")


def validate_admin_user(value):
    if isinstance(value, int):
        user = User.objects.filter(id=value).first()
    else:
        user = value

    if user is None or user.user_type != 2:
        raise ValidationError("Only admin users can create polls.")


class Poll(models.Model):
    """
    A single poll.
    """
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, validators=[MinLengthValidator(3)])
    question = models.TextField()
    expiry_date = models.DateTimeField(validators=[validate_expiry_date])
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, related_name='polls', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   related_name='created_polls', validators=[validate_admin_user])

    def __str__(self):
        return str(self.id) + ': ' + str(self.title)

    class Meta:
        db_table = "poll"


class Choice(models.Model):
    """
    A choice in a poll.
    """
    id = models.AutoField(primary_key=True)
    poll = models.ForeignKey(Poll, related_name='choices', on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200, validators=[MinLengthValidator(2)])
    vote_count = models.IntegerField(default=0)

    def __str__(self):
        return str(self.id) + ': ' + str(self.choice_text)

    class Meta:
        db_table = "choice"
        unique_together = ('poll', 'choice_text')

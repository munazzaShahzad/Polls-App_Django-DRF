import enum

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Tag(models.Model):
    tag_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Poll(models.Model):
    poll_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    question = models.TextField()
    expiry_date = models.DateTimeField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, related_name='polls', blank=True)

    def __str__(self):
        return self.question


class Choice(models.Model):
    choice_id = models.AutoField(primary_key=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)

    def __str__(self):
        return self.choice_text


class User(AbstractUser):
    class UserTypeEnum(enum.Enum):
        ADMIN = 'ADMIN'
        REGULAR = 'REGULAR'

    user_id = models.AutoField(primary_key=True)
    user_type = models.CharField(
        max_length=10,
        choices=UserTypeEnum.choices(),
        default=UserTypeEnum.REGULAR.value
    )

    def __str__(self):
        return self.username


class UserPollHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    voting_time = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'poll')


class UserTagHistory(models.Model):
    user = models.ForeignKey(User, primary_key=True, on_delete=models.CASCADE)
    tag_history = models.JSONField(default=dict)

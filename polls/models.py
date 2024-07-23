from enum import IntEnum
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "category"


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "tag"


class Poll(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    question = models.TextField()
    expiry_date = models.DateTimeField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, related_name='polls', blank=True)

    def __str__(self):
        return self.question

    class Meta:
        db_table = "poll"


class Choice(models.Model):
    id = models.AutoField(primary_key=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)

    def __str__(self):
        return self.choice_text

    class Meta:
        db_table = "choice"


class User(AbstractUser):
    class UserTypeEnum(IntEnum):
        REGULAR = 1
        ADMIN = 2

        @classmethod
        def choices(cls):
            return [(key.value, key.name) for key in cls]

    id = models.AutoField(primary_key=True)
    user_type = models.CharField(
        max_length=10,
        choices=UserTypeEnum.choices(),
        default=UserTypeEnum.REGULAR.value
    )

    def __str__(self):
        return self.username

    class Meta:
        db_table = "user"


class UserPollHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    voting_time = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'poll')
        db_table = "user_poll_history"


class UserTagHistory(models.Model):
    user = models.ForeignKey(User, primary_key=True, on_delete=models.CASCADE)
    tag_history = models.JSONField(default=dict)

    class Meta:
        db_table = "user_tag_history"

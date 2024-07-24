from django.db import models
from django.contrib.auth.models import AbstractUser
from enum import IntEnum


class User(AbstractUser):
    class UserTypeEnum(IntEnum):
        REGULAR = 1
        ADMIN = 2

        @classmethod
        def choices(cls):
            return [(key.value, key.name) for key in cls]

    id = models.AutoField(primary_key=True)
    user_type = models.IntegerField(
        max_length=10,
        choices=UserTypeEnum.choices(),
        default=UserTypeEnum.REGULAR.value
    )

    def __str__(self):
        return self.username

    class Meta:
        db_table = "user"

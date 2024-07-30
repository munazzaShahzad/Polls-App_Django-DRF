from enum import IntEnum

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    class UserTypeEnum(IntEnum):
        REGULAR = 1
        ADMIN = 2

        @classmethod
        def choices(cls):
            return [(key.value, key.name) for key in cls]

    id = models.AutoField(primary_key=True)
    user_type = models.IntegerField(
        choices=UserTypeEnum.choices(),
        default=UserTypeEnum.REGULAR.value,
        validators=[MinValueValidator(1), MaxValueValidator(2)]
    )

    def __str__(self):
        return str(self.id) + ': ' + str(self.username)

    class Meta:
        db_table = "user"

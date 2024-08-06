from enum import IntEnum

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    """
    Custom user object
    """
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


@receiver(post_save, sender=User)
def set_admin_user(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 2:
            instance.is_staff = True
            instance.save(update_fields=['is_staff'])
    else:
        if instance.user_type == 2 and not instance.is_staff:
            instance.is_staff = True
            instance.save(update_fields=['is_staff'])
        elif instance.user_type != 2 and instance.is_staff:
            instance.is_staff = False
            instance.save(update_fields=['is_staff'])

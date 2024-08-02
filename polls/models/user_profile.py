from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from .user import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=255)
    email = models.EmailField()
    role = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name}'s Profile"

    class Meta:
        db_table = "user_profile"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    full_name = f"{instance.first_name} {instance.last_name}".strip()
    if created:
        UserProfile.objects.create(user=instance, name=full_name, email=instance.email, role=instance.get_user_type_display())
    else:
        profile, profile_created = UserProfile.objects.get_or_create(user=instance)
        profile.name = full_name
        profile.email = instance.email
        profile.role = instance.get_user_type_display().title()
        profile.save()

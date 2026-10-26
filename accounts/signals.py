from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=User)
#runs after any User is saved whether from signup page or admin.
def create_profile(sender, instance, created, **kwargs):
    if created: #created is True only the first time
        Profile.objects.create(user=instance)
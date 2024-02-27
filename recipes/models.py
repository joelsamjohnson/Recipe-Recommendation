from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class Recipe(models.Model):
    title = models.CharField(max_length=200, default='Untitled Recipe')
    desc = models.TextField(default='No description provided.',null=True,blank=True)
    rating = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    ingredients = models.JSONField(default=list)
    directions = models.JSONField(default=list)
    categories = models.JSONField(default=list)
    date = models.CharField(max_length=200, default='No date provided')
    image_url = models.URLField(max_length=1024, blank=True, null=True)
    # Nutritional information fields
    calories = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    fat = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    protein = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    sodium = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    preferences = models.JSONField(default=list, blank=True)  # Using JSONField to store a list of preferences

    def get_preferences(self):
        return self.preferences

    def set_preferences(self, preferences):
        self.preferences = preferences
        self.save()

# Ensure a UserProfile is created whenever a User instance is created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.profile.save()

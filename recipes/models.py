from django.db import models
from django.conf import settings


class Recipe(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True,blank=True)
    rating = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    total_time = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    ingredients = models.JSONField(default=list)
    directions = models.JSONField(default=list)
    categories = models.JSONField(default=list)
    tags = models.JSONField(default=list)
    date = models.DateField(auto_now_add=True)
    image_url = models.URLField(max_length=1024, blank=True, null=True)
    calories = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    fat = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    protein = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    sodium = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.title

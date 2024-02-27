from django.core.management.base import BaseCommand
from ...models import Recipe  # Adjust the import path according to your app's structure
from ...utils import search_recipe


class Command(BaseCommand):
    help = 'Updates recipe images in the database by scraping them from the web.'

    def handle(self, *args, **options):
        recipes = Recipe.objects.all()
        for recipe in recipes:
            try:
                name = recipe.title
                if recipe.image_url:
                    pass
                else:
                    recipe_url = search_recipe(name)
                    recipe.image_url = recipe_url
                    recipe.save()
                    print(f"Updated image URL for {recipe.title}")
            except Exception as e:
                print(f"Failed to update {recipe.title}: {e}")

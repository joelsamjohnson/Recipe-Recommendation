# load_recipes.py
import json
from django.core.management.base import BaseCommand
from ...models import Recipe  # Adjust the import based on your app and model name
from decimal import Decimal, InvalidOperation

def safe_convert_to_decimal(value):
    try:
        return Decimal(value) if value is not None else None
    except InvalidOperation:
        print(f"Warning: Unable to convert value '{value}' to Decimal.")
        return None

class Command(BaseCommand):
    help = 'Load a list of recipes from a JSON file into the database'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str)

    def handle(self, *args, **options):
        with open(options['json_file'], 'r', encoding='utf-8') as file:
            data = json.load(file)

            for recipe_data in data:
                title = recipe_data.get('title')
                if not title:  # Checks if title is None or an empty string
                    self.stdout.write(self.style.WARNING(f"Skipping recipe due to missing title: {recipe_data}"))
                    continue

                # Convert numerical values safely
                fat = safe_convert_to_decimal(recipe_data.get('fat'))
                calories = safe_convert_to_decimal(recipe_data.get('calories'))
                protein = safe_convert_to_decimal(recipe_data.get('protein'))
                sodium = safe_convert_to_decimal(recipe_data.get('sodium'))

                # Prepare other fields
                directions = recipe_data.get('directions', [])
                date = recipe_data.get('date', None)
                categories = recipe_data.get('categories', [])
                desc = recipe_data.get('desc', None)
                rating = recipe_data.get('rating', 0)
                ingredients = recipe_data.get('ingredients', [])

                # Check for None values in critical Decimal fields to skip invalid recipes
                if None in (fat, calories, protein, sodium):
                    self.stdout.write(self.style.ERROR(f"Skipping recipe due to invalid numerical conversion: {recipe_data}"))
                    continue

                try:
                    Recipe.objects.create(
                        title=title,
                        directions='\n'.join(directions),
                        fat=fat,
                        date=date,
                        categories=categories,
                        calories=calories,
                        desc=desc,
                        protein=protein,
                        rating=rating,
                        ingredients=ingredients,
                        sodium=sodium,
                    )
                except Exception as e:  # Catch any other exception during recipe creation
                    self.stdout.write(self.style.ERROR(f'Error loading recipe: {e} - {recipe_data}'))
                    continue  # Skip to the next recipe

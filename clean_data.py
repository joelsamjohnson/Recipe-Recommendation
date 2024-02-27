import json

def clean_numeric_value(value):
    """Attempt to clean numeric fields and return a standardized float or None."""
    try:
        value = value.replace(',', '.')  # Replace commas with dots for decimal
        return float(value)
    except ValueError:
        return None

# Assuming data is a list of dictionaries loaded from your JSON file
cleaned_data = []
for recipe in data:
    recipe['calories'] = clean_numeric_value(recipe.get('calories'))
    recipe['calories'] = clean_numeric_value(recipe.get('calories'))
    recipe['calories'] = clean_numeric_value(recipe.get('calories'))
    recipe['calories'] = clean_numeric_value(recipe.get('calories'))
    recipe['calories'] = clean_numeric_value(recipe.get('calories'))

    # Repeat for other numeric fields
    cleaned_data.append(recipe)

# Write cleaned_data to a new file or proceed to import it into your Django model

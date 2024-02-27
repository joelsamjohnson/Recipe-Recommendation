from django.core.serializers import serialize
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.http import JsonResponse
from django.db.models import F
from .models import Recipe,UserProfile
from .serializers import RecipeSerializer
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import sigmoid_kernel
import json
import datetime

df = pd.read_csv('epi_r.csv')
upper = df['title']
lower = df['title'].str.lower()
df['title'] = lower
# Add any non-tag columns here
exclude_columns = ['title', 'rating', 'calories', 'protein', 'fat', 'sodium']
tag_columns = [col for col in df.columns if col not in exclude_columns]


def create_bag_of_words(row):
    # Filter tags based on their value and concatenate them into a single string
    tags_present = ' '.join([col.lower() for col in tag_columns if row[col] > 0])
    # Concatenate the title with the tags
    return row['title'] + ' ' + tags_present


# Apply the function to each row
df['bag'] = df.apply(create_bag_of_words, axis=1)

# At this point, df['bag'] contains a 'bag of words' for each recipe, including the title and all present tags.
tfv = TfidfVectorizer(min_df=3, max_features=None, strip_accents='unicode', analyzer='word', token_pattern=r'\w{1,}',
                      ngram_range=(1, 3), stop_words='english')
df['bag'] = df['bag'].fillna('')
tfv_matrix = tfv.fit_transform(df['bag'])
sig = sigmoid_kernel(tfv_matrix, tfv_matrix)
indices = pd.Series(df.index, index=df['title']).drop_duplicates()

MEAL_TAGS = {
    # Example tags, replace with actual ones
    'breakfast': ['breakfast'],
    'lunch': ['lunch'],
    'dinner': ['dinner'],
    'snack': ['snack'],
    # Add more mappings as needed
}


@api_view(['GET'])
def all_data(request):
    # Assuming 'df' contains the basic recipe data like titles and ratings
    data = pd.DataFrame(df[['title', 'rating', 'calories']])

    # Fetch all recipes that match the titles in the DataFrame
    titles = data['title'].tolist()
    recipes = Recipe.objects.filter(title__in=titles)

    # Convert the QuerySet to a list of dictionaries for easier processing
    recipes_list = list(recipes.values('title', 'image_url', 'desc'))

    # Create a dictionary for quick lookup by title
    recipes_dict = {recipe['title']: recipe for recipe in recipes_list}

    # Add 'image_url' and 'desc' to the DataFrame
    data['image_url'] = data['title'].apply(lambda title: recipes_dict.get(title, {}).get('image_url', ''))
    data['desc'] = data['title'].apply(lambda title: recipes_dict.get(title, {}).get('desc', ''))

    return_data = data.to_json(orient="records")
    parsed = json.loads(return_data)
    response = json.dumps(parsed, indent=4)  # Pretty print the JSON
    return Response(json.loads(response))


@api_view(['POST'])
def recommend_recipe(request):
    if request.method == 'POST':
        try:
            request_data = request.data
            title = request_data.get('title')

            # Find the recipe in the database
            try:
                main_recipe = Recipe.objects.get(title__iexact=title)
            except Recipe.DoesNotExist:
                return Response({"response": "Recipe title not found."}, status=404)

            idx = indices[title]
            sig_scores = list(enumerate(sig[idx]))
            sig_scores = sorted(sig_scores, key=lambda x: x[1], reverse=True)
            recipes_indices = [i[0] for i in sig_scores[1:11]]

            similar_recipes = Recipe.objects.filter(id__in=recipes_indices).values('title','image_url', 'rating')

            similar_recipes_list = list(similar_recipes)
            return Response(similar_recipes_list)
        except Exception as e:
            return Response({"response": "Error processing your request.", "detail": str(e)}, status=400)


@api_view(['GET', 'POST'])
def time_based_recipes(request):
    try:
        now = datetime.datetime.now()
        current_hour = now.hour

        # Determine the meal type based on the current time
        if 5 <= current_hour < 10:
            meal_type = 'breakfast'
        elif 10 <= current_hour < 14:
            meal_type = 'lunch'
        elif 14 <= current_hour < 17:
            meal_type = 'snack'
        elif 17 <= current_hour < 21:
            meal_type = 'dinner'
        else:
            meal_type = 'snack'

        relevant_tags = MEAL_TAGS.get(meal_type, [])

        # Filter recipes based on relevant tags
        filtered_recipes = df[df[relevant_tags].sum(axis=1) > 0]

        # Create a list of recipe titles from the filtered DataFrame
        titles = filtered_recipes['title'].tolist()

        # Fetch image_url and desc from the database for these titles
        recipes_in_db = Recipe.objects.filter(title__in=titles).values(
            'title',  # Assuming you want to keep the original field name here
            'image_url',
            'desc',  # Assuming the field is named 'description' in your model
            'rating',  # Assuming there's a 'rating' field in your model
            'calories'  # Assuming there's a 'calories' field in your model
        )

        # Convert the QuerySet to a list of dictionaries
        recipes_list = list(recipes_in_db)

        return Response(recipes_list)
    except Exception as e:
        return Response({"error": str(e)}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class RecipeList(View):
    def get(self, request):
        recipes = Recipe.objects.all()
        recipes_json = serialize('json', recipes)
        return JsonResponse(recipes_json, safe=False)

    def post(self, request):
        data = json.loads(request.body)
        recipe = Recipe.objects.create(
            title=data.get('title'),
            desc=data.get('desc'),
            rating=data.get('rating'),
            ingredients=data.get('ingredients'),
            directions=data.get('directions'),
            categories=data.get('categories')
        )
        return JsonResponse({'message': 'Recipe created successfully', 'id': recipe.id})


def extract_tags_from_recipe(df, recipe_id):
    """
    Extracts tags from a specific recipe in the dataframe.
    :param df: DataFrame containing the recipe data.
    :param recipe_id: Unique identifier for the recipe.
    :return: List of tags for the given recipe.
    """
    # Assuming `recipe_id` can directly index the DataFrame or maps to it.
    recipe_row = df.loc[recipe_id]
    tags = [col.lower() for col in tag_columns if recipe_row[col] > 0]
    return tags


@method_decorator(csrf_exempt, name='dispatch')
class RecipeDetailView(RetrieveAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        self.update_user_preferences(request.user, instance)
        # Return the serialized recipe
        return Response(serializer.data)

    def update_user_preferences(user_id, recipe_id, df):
        userprofile = UserProfile.objects.get(id=user_id)
        recipe_tags = extract_tags_from_recipe(df, recipe_id)
        current_preferences = userprofile.get_preferences()
        updated_preferences = list(set(current_preferences + recipe_tags))
        userprofile.set_preferences(updated_preferences)


class RecipeSearchView(APIView):
    def get(self, request):
        query = request.query_params.get('query', None)
        if query:
            recipes = Recipe.objects.filter(title__icontains=query)
            serializer = RecipeSerializer(recipes, many=True)
            return Response(serializer.data)
        else:
            return Response({"message": "No query provided."})


@require_http_methods(["GET", "POST"])
def get_final_data(request):
    if request.method == "POST":
        try:
            details = json.loads(request.body)
            iid = details.get('id')
            user = User.objects.filter(user_id=iid).first()
            if user:
                # Assuming 'preferences' is where the options are stored in your User model
                l = ast.literal_eval(user.preferences)
                # This assumes 'Tags' is stored in an ArrayField or similar; adjust querying logic based on your actual model
                recipes = Recipe.objects.filter(Tags__overlap=l)[:300]

                data = list(recipes.values('RecipeID', 'recipes', 'ImageLink', 'Description', 'Tags', 'Nutritions', 'By', 'RequiredTime', 'Servings', 'Ingredients', 'Directions'))
                return JsonResponse(data, safe=False)  # Returns the data as JSON
            else:
                return JsonResponse({"response": False}, status=404)
        except Exception as e:
            return JsonResponse({"response": False, "error": str(e)}, status=400)
    else:
        # For a GET request, or any non-POST request, you might want to return a simple error or redirect.
        return JsonResponse({"response": "This endpoint only supports POST requests."}, status=405)

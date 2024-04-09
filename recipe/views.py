from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from .models import Recipe, RecipeLike, RecipeComment
from followers.models import Follower
from .serializers import RecipeLikeSerializer, RecipeSerializer, RecipeCommentSerializer
from .permissions import IsAuthorOrReadOnly
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import filters
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema, OpenApiParameter, inline_serializer
from drf_spectacular.types import OpenApiTypes
import requests
import datetime

headers = {
	"X-RapidAPI-Key": "0a6b63336amshbafb527ce18a6c9p184c71jsnaa99550c9707",
	"X-RapidAPI-Host": "yummly2.p.rapidapi.com"
}

@extend_schema(
    description="Retrieve a list of all recipes. Filters can be applied.",
    parameters=[
        OpenApiParameter(name='category__name', description='Filter by recipe category name', required=False, type=OpenApiTypes.STR),
        OpenApiParameter(name='author__username', description='Filter by author username', required=False, type=OpenApiTypes.STR),
    ],
    responses={200: RecipeSerializer(many=True)}
)
class RecipeListAPIView(generics.ListAPIView):
    """
    Get: a collection of recipes
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AllowAny,)
    filterset_fields = ('category__name', 'author__username')


@extend_schema(
    description="Create a new recipe.",
    request=RecipeSerializer,
    responses={
        201: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT
    }
)
class RecipeCreateAPIView(generics.CreateAPIView):
    """
    Create: a recipe
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        self.status = status.HTTP_201_CREATED

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            "status": 1,
            "data": serializer.data,
            "msg": "Recipe successfully created"
        }, status=status.HTTP_201_CREATED, headers=headers)


@extend_schema(
    description="Retrieve, update, or delete a recipe.",
    responses={
        200: RecipeSerializer,
        404: OpenApiTypes.OBJECT
    }
)
class RecipeAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, Update, Delete a recipe
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)


@extend_schema(
    description="Like or unlike a recipe.",
    methods=['POST'],
    responses={
        201: {"description": "Recipe liked successfully."},
        400: {"description": "You already liked this recipe or like not found."},
    }
)
@extend_schema(
    description="Remove a like from a recipe.",
    methods=['DELETE'],
    responses={
        200: {"description": "Like removed successfully."},
        400: {"description": "Like not found."},
    }
)
class RecipeLikeAPIView(generics.CreateAPIView):
    """
    Like, Dislike a recipe
    """
    serializer_class = RecipeLikeSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
        new_like, created = RecipeLike.objects.get_or_create(
            user=request.user, recipe=recipe)
        if created:
            new_like.save()
            return Response({"status": 1,"message": "Recipe liked successfully."}, status=status.HTTP_201_CREATED)
        return Response({"status": 0,"message": "You already liked this recipe."}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
        like = RecipeLike.objects.filter(user=request.user, recipe=recipe)
        if like.exists():
            like.delete()
            return Response({"status": 1,"message": "Like removed successfully."}, status=status.HTTP_200_OK)
        return Response({"status": 0,"message": "Like not found."}, status=status.HTTP_400_BAD_REQUEST)
        

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


@extend_schema(
    description="List or create comments for a specific recipe.",
    responses={
        200: RecipeCommentSerializer(many=True),
        201: RecipeCommentSerializer,
        400: OpenApiTypes.OBJECT
    }
)
class RecipeCommentAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = RecipeComment.objects.all()
    serializer_class = RecipeCommentSerializer

    def get_queryset(self):
        recipe_id = self.kwargs.get('pk')
        return RecipeComment.objects.filter(recipe_id=recipe_id)

    def post(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, recipe_id=pk)
            return Response({'status': 1, 'message': 'Comment created successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'status': 0, 'message': 'Comment not added', 'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


@extend_schema(
    description="List or create comments on recipes.",
    responses={
        200: RecipeCommentSerializer(many=True),
    }
)
class CommentsonRecipesView(generics.ListCreateAPIView):
    queryset = RecipeComment.objects.all()
    serializer_class = RecipeCommentSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        recipe_id = self.kwargs.get('recipe_id')
        if recipe_id:
            queryset = queryset.filter(recipe_id=recipe_id)
        return queryset


@extend_schema(
    description="Retrieve or create recipes for the authenticated user.",
    responses={
        200: RecipeSerializer(many=True),
        201: RecipeSerializer,
        400: OpenApiTypes.OBJECT
    }
)
class MyRecipeView(generics.ListCreateAPIView):
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'category_name']

    def get_queryset(self):
        return Recipe.objects.filter(author=self.request.user)


@extend_schema(
    description="Retrieve a feed of recipes from users the authenticated user is following.",
    responses={
        200: RecipeSerializer(many=True),
    }
)
class FeedAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        following_users = Follower.objects.filter(from_user=request.user).values_list('to_user_id', flat=True)
        recipes = Recipe.objects.filter(author__in=following_users).order_by('-created_at')
        serializer = RecipeSerializer(recipes, many=True)
        return Response(serializer.data)


@extend_schema(
    description='Autocomplete API for Yummly',
    summary='Yummly Autocomplete',
    parameters=[
        OpenApiParameter(name='query', description='Query string for searching recipes', required=True, type=OpenApiTypes.STR)
    ],
    responses={
        200: inline_serializer(
            name='YummlyAutocompleteResponse',
            fields={
                'some_field': OpenApiTypes.STR,
                # Define the structure of your response here.
                # Replace 'some_field' and its type with the actual fields from your JSON response.
            }
        ),
        500: OpenApiTypes.OBJECT
    }
)
@api_view(['GET'])
def yummly_autocomplete(request):
    query = request.GET.get('query', '')
    url = "https://yummly2.p.rapidapi.com/feeds/auto-complete"
    response = requests.get(url, headers=headers, params={"q": query})
    if response.status_code == 200:
        data = response.json()
        return JsonResponse(data, safe=False)
    else:
        return JsonResponse({"error": "Failed to fetch data from Yummly2 API"}, status=500)



@csrf_exempt
@extend_schema(
    description='Search API for Yummly',
    summary='Yummly Search',
    parameters=[
        OpenApiParameter(name='query', description='Search query', required=True, type=OpenApiTypes.STR),
        OpenApiParameter(name='start', description='Start index', required=False, type=OpenApiTypes.INT, default=0),
        OpenApiParameter(name='maxResults', description='Maximum number of results to return', required=False, type=OpenApiTypes.INT, default=3)
    ],
    responses={
        200: inline_serializer(
            name='YummlySearchResponse',
            fields={
                'some_field': OpenApiTypes.STR,
                'title': OpenApiTypes.STR,
                'image_url': OpenApiTypes.STR,
                'total_time': OpenApiTypes.STR,
                'tags': {
                    'course': OpenApiTypes.STR,
                    'cuisine': OpenApiTypes.STR,
                    'holiday': OpenApiTypes.STR,
                    'technique': OpenApiTypes.STR
                },
                'preparation_steps': OpenApiTypes.STR,
                # 'resizable_image_url': resizable_image_url,
                'ingredient_lines': OpenApiTypes.STR,
                }
        ),
        500: OpenApiTypes.OBJECT
    }
)
@api_view(['GET'])
def yummly_search(request):
    query = request.GET.get('query', '')
    start = request.GET.get('start', '0')
    maxResults = request.GET.get('maxResults', '20 ')
    url = "https://yummly2.p.rapidapi.com/feeds/search"
    params = {"q": query,"start": start,"maxResult": maxResults,}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        parsed_recipes = []
        for item in data.get('feed', []):
            title = item.get('content', {}).get('details', {}).get('name')
            image_url = item.get('content', {}).get('details', {}).get('images', [{}])[0].get('hostedLargeUrl')
            total_time = item.get('content', {}).get('details', {}).get('totalTime')
            tags = item.get('content', {}).get('tags', {})
            course = [{'display-name': tag.get('display-name'), 'tag-url': tag.get('tag-url')} for tag in tags.get('course', [])]
            cuisine = [{'display-name': tag.get('display-name'), 'tag-url': tag.get('tag-url')} for tag in tags.get('cuisine', [])]
            holiday = [{'display-name': tag.get('display-name'), 'tag-url': tag.get('tag-url')} for tag in tags.get('holiday', [])]
            technique = [{'display-name': tag.get('display-name'), 'tag-url': tag.get('tag-url')} for tag in tags.get('technique', [])]
            preparation_steps = item.get('content', {}).get('preparationSteps', [])
            # resizable_image_url = item.get('content', {}).get('details', {}).get('images', [{}])[0].get('resizableImageUrl')
            ingredient_lines = [ line.get('wholeLine') for line in item.get('content', {}).get('ingredientLines', [])]
    
            parsed_recipe = {
                'title': title,
                'image_url': image_url,
                'total_time':total_time,
                'tags': {
                    'course': course,
                    'cuisine': cuisine,
                    'holiday': holiday,
                    'technique': technique
                },
                'preparation_steps': preparation_steps,
                # 'resizable_image_url': resizable_image_url,
                'ingredient_lines': ingredient_lines
            }
        
            # Adding the parsed recipe to the list
            parsed_recipes.append(parsed_recipe)
    
        # Returning the parsed recipes as a JSON response
        return JsonResponse({"data":parsed_recipes}, safe=False)
    else:
        return JsonResponse({"error": "Failed to fetch data from Yummly2 API"}, status=response.status_code)


@csrf_exempt
@extend_schema(
    description='Fetch feeds list from Yummly based on tags',
    summary='Yummly Feeds List',
    parameters=[
        OpenApiParameter(name='start', description='Start index for fetching feeds', required=False, type=OpenApiTypes.INT, default=0),
        OpenApiParameter(name='limit', description='Number of feeds to fetch', required=False, type=OpenApiTypes.INT, default=1),
        OpenApiParameter(name='tag', description='Tag to filter feeds', required=False, type=OpenApiTypes.STR, default='')
    ],
    responses={
        200: inline_serializer(
            name='YummlyFeedsListResponse',
            fields={
                'some_field': OpenApiTypes.STR,
                # Define the structure of your response here
                # Replace 'some_field' and its type with the actual fields from your JSON response
            }
        ),
        500: OpenApiTypes.OBJECT
    }
)
@api_view(["GET"])
def category_feed(request):
    start = request.GET.get('start', '0')
    limit = request.GET.get('limit', '10')
    tag = request.GET.get('tag', '')

    url = "https://yummly2.p.rapidapi.com/feeds/list"

    params = {
        "start": start,
        "limit": limit,
        "tag": tag
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
        
            filtered_data = []
            for item in data.get('feed', []):
                content = item.get('content', {})
                details = content.get('details', {})
                tags = content.get('tags', {})
                images = details.get('images', [])
                ingredients_info = content.get('ingredientLines', [])  # Get the ingredients part
                ingredients = [ingredient.get('wholeLine') for ingredient in ingredients_info]

                recipe_info = {
                    'title': item.get('display', {}).get('displayName'),  # Assuming you meant the recipe name here
                    'description': content.get('description', {}).get('text'),
                    'image': images[0].get('hostedLargeUrl') if images else None,
                    'ingredients':ingredients,
                    'preparationSteps': content.get('preparationSteps', []),
                    'course': [tag.get('display-name') for tag in tags.get('course', [])],
                    'difficulty': [tag.get('display-name') for tag in tags.get('difficulty', [])],
                    'nutrition': [tag.get('display-name') for tag in tags.get('nutrition', [])],
                    'technique': [tag.get('display-name') for tag in tags.get('technique', [])],
                    'total_time': details.get('totalTime'),
                    'rating': details.get('rating'),
                    'author': details.get('displayName')
                }
                
                filtered_data.append(recipe_info)
        
            return JsonResponse(filtered_data, safe=False)
        else:
            return JsonResponse({"error": "Failed to fetch data from Yummly2 API", "status_code": response.status_code}, status=response.status_code)
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)
    

def yummly_feeds_list(start, limit, tag=''):
    url = "https://yummly2.p.rapidapi.com/feeds/list"
    params = {"start": start, "limit": limit, "tag": tag }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        filtered_data = []
        for item in data.get('feed', []):
            details = item.get('content', {}).get('details', {})
            content = item.get('content', {})
            ingredients_info = content.get('ingredientLines', [])  # Get the ingredients part

            # Process ingredients to extract name and amount in imperial format
            ingredients = []
            for ingredient in ingredients_info:
                ingredient_name = ingredient.get('ingredient')
                amount_imperial = ingredient.get('amount', {}).get('imperial', {})
                quantity_imperial = amount_imperial.get('quantity')
                unit_imperial = amount_imperial.get('unit', {}).get('abbreviation', '')
                
                ingredients.append(f"{quantity_imperial} {unit_imperial} {ingredient_name}")

            recipe = {
                'name': details.get('name'),
                'image': details.get('images', [{}])[0].get('resizableImageUrl'),
                'totalTime': details.get('totalTime'),
                'preparationSteps': content.get('preparationSteps', []),
                'ingredients': ingredients,  # Adjusted to include only names and amounts in imperial
                'rating': details.get('rating')
            }
            filtered_data.append(recipe)
        
        return JsonResponse({"data":filtered_data}, safe=False)
    else:
        return JsonResponse({"error": "Failed to fetch data from Yummly2 API"}, status=response.status_code)

@csrf_exempt
@require_http_methods(["GET"])  # Only allow GET requests for this view
def get_list_similarities(request):
    url = "https://yummly2.p.rapidapi.com/feeds/list-similarities"
    params = request.GET.dict()
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        return JsonResponse(data, safe=False)
    else:
        return JsonResponse({"error": "Failed to fetch data from the API"}, status=response.status_code)

@csrf_exempt
@extend_schema(
    description='Fetch categories list from Yummly',
    summary='Yummly Categories List',
    responses={
        200: inline_serializer(
            name='YummlyCategoriesListResponse',
            fields={
                'categories': OpenApiTypes.OBJECT,  # Adjust based on actual response structure
                # Define the structure of your response here
            }
        ),
        500: OpenApiTypes.OBJECT
    }
)
@api_view(['GET'])
def get_categories_list(request):
    url = "https://yummly2.p.rapidapi.com/categories/list"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        # Initialize an empty list to hold the simplified categories
        simplified_categories = []
        
        # Iterate through the categories in the response
        for category in data.get("browse-categories", []):
            # Extract the required fields
            tracking_id = category.get("tracking-id")
            display_name = category.get("display", {}).get("displayName")
            category_image = category.get("display", {}).get("categoryImage")
            tag = category.get("display", {}).get("tag")
            
            # Add the simplified category to the list
            simplified_categories.append({
                "tracking-id": tracking_id,
                "display name": display_name,
                "category image": category_image,
                "tag": tag
            })
        
        # Return the simplified categories as a JsonResponse
        return JsonResponse({"data":simplified_categories})
    else:
        return JsonResponse({"error": "Failed to fetch data from Yummly2 API"}, status=response.status_code)


@extend_schema(
    description='Fetch feeds list from Yummly based on the current time of day.',
    summary='Yummly Time-Based Feeds List',
    parameters=[
        OpenApiParameter(name='start', description='Start index for fetching feeds', required=False, type=OpenApiTypes.INT, default=0),
        OpenApiParameter(name='limit', description='Number of feeds to fetch', required=False, type=OpenApiTypes.INT, default=10),
    ],
    responses={
        200: {
"type": "object",

        },
        500: OpenApiTypes.OBJECT
    }
)
@api_view(['GET'])
def time_based_yummly_feeds(request):
        now = datetime.datetime.now()
        hour = now.hour
        tag = ''

        if hour < 12:
            tag = 'list.recipe.search_based:fq:attribute_s_mv:course^course-Breakfast and Brunch'
        elif 12 <= hour < 15:
            tag = 'list.recipe.search_based:fq:attribute_s_mv:course^course-Lunch'
        elif 15 <= hour < 20:
            tag='list.recipe.search_based: fq:attribute_s_mv: (dish\\ ^ dish\\-cake)'
        elif 20 <= hour < 23:
            tag = 'list.recipe.search_based:fq:attribute_s_mv:(course^course-Main Dishes)'
        else:
            tag = 'list.recipe.search_based:fq:attribute_s_mv:course^course-Breakfast and Brunch'
        return yummly_feeds_list(0,5,tag)


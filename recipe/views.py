from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Recipe, RecipeLike, RecipeComment
from followers.models import Follower
from .serializers import RecipeLikeSerializer, RecipeSerializer, RecipeCommentSerializer
from .permissions import IsAuthorOrReadOnly


class RecipeListAPIView(generics.ListAPIView):
    """
    Get: a collection of recipes
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AllowAny,)
    filterset_fields = ('category__name', 'author__username')


class RecipeCreateAPIView(generics.CreateAPIView):
    """
    Create: a recipe
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class RecipeAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, Update, Delete a recipe
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)


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
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
        like = RecipeLike.objects.filter(user=request.user, recipe=recipe)
        if like.exists():
            like.delete()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class RecipeCommentAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = RecipeComment.objects.all()
    serializer_class = RecipeCommentSerializer

    def get_queryset(self):
        recipe_id = self.kwargs.get('pk')
        return RecipeComment.objects.filter(recipe_id=recipe_id)

    def post(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs.get('pk'))
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
        comment = RecipeComment.objects.filter(user=request.user, recipe=recipe)
        if comment.exists():
            comment.delete()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


    def perform_create(self, serializer):
        recipe = Recipe.objects.get(id=self.kwargs['recipe_id'])
        serializer.save(user=self.request.user, recipe=recipe)


class CommentsonRecipesView(generics.ListCreateAPIView):
    queryset = RecipeComment.objects.all()
    serializer_class = RecipeCommentSerializer

    def get_queryset(self):
        queryset = RecipeComment.objects.all()
        recipe_id = self.kwargs.get('recipe_id')
        if recipe_id:
            queryset = queryset.filter(recipe__comment__id=comment_id)
        return queryset

class MyRecipeView(generics.ListCreateAPIView):
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticated,)


    def get_queryset(self):
        return Recipe.objects.filter(author=self.request.user)


class FeedAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        following_users = Follower.objects.filter(from_user=request.user).values_list('to_user_id', flat=True)
        recipes = Recipe.objects.filter(author__in=following_users).order_by('-created_at')
        serializer = RecipeSerializer(recipes, many=True)
        return Response(serializer.data)


from django.http import JsonResponse
import requests
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

headers = {
	"X-RapidAPI-Key": "a2902d5316msh18425308907ed14p12fb8cjsn00f739bb744d",
	"X-RapidAPI-Host": "yummly2.p.rapidapi.com"
}

@csrf_exempt
def yummly_autocomplete(request):
    # Check for a query parameter in the request
    query = request.GET.get('query', '')

    # Define the URL and the headers required by the Yummly2 API
    url = "https://yummly2.p.rapidapi.com/feeds/auto-complete"


    # Send a request to the Yummly2 API
    response = requests.get(url, headers=headers, params={"q": query})

    # Check if the request was successful
    if response.status_code == 200:
        # Convert the response to JSON
        data = response.json()
        # Return the JSON data as a JsonResponse
        return JsonResponse(data, safe=False)
    else:
        # If the request was not successful, return an error message
        return JsonResponse({"error": "Failed to fetch data from Yummly2 API"}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def yummly_search(request):
    query = request.GET.get('query', '')
    start = request.GET.get('start', '0')
    maxResults = request.GET.get('maxResults', '3')
    url = "https://yummly2.p.rapidapi.com/feeds/search"
    params = {
        "q": query,
        "start": start,
        "maxResult": maxResults,
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            return JsonResponse(data, safe=False)
        else:
            return JsonResponse({"error": "Failed to fetch data from Yummly2 API", "status_code": response.status_code}, status=response.status_code)
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def yummly_feeds_list(request):
    start = request.GET.get('start', '0')
    limit = request.GET.get('limit', '1')
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
            return JsonResponse(data, safe=False)
        else:
            return JsonResponse({"error": "Failed to fetch data from Yummly2 API", "status_code": response.status_code}, status=response.status_code)
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])  # Only allow GET requests for this view
def get_list_similarities(request):
    url = "https://yummly2.p.rapidapi.com/feeds/list-similarities"
    params = request.GET.dict()

    try:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            return JsonResponse(data, safe=False)
        else:
            return JsonResponse({"error": "Failed to fetch data from the API", "status_code": response.status_code},
                                status=response.status_code)
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_categories_list(request):

    url = "https://yummly2.p.rapidapi.com/categories/list"
    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return JsonResponse(data, safe=False)
        else:

            return JsonResponse({"error": "Failed to fetch data from Yummly2 API", "status_code": response.status_code}, status=response.status_code)
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)



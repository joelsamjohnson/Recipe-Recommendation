from django.urls import path

from .views import RecipeCreateAPIView, RecipeListAPIView, RecipeAPIView, RecipeLikeAPIView, RecipeCommentAPIView, CommentsonRecipesView, MyRecipeView, FeedAPIView, yummly_autocomplete, category_feed, yummly_feeds_list, yummly_search, get_categories_list, get_list_similarities, time_based_yummly_feeds

app_name = 'recipe'

urlpatterns = [
    path('', RecipeListAPIView.as_view(), name="recipe-list"),
    path('<int:pk>/', RecipeAPIView.as_view(), name="recipe-detail"),
    path('create/', RecipeCreateAPIView.as_view(), name="recipe-create"),
    path('<int:pk>/like/', RecipeLikeAPIView.as_view(), name='recipe-like'),
    path('<int:pk>/comment/', RecipeCommentAPIView.as_view(), name='recipe-comment'),
    path('<int:recipe_id>/comments/', CommentsonRecipesView.as_view(), name='recipe-comments'),
    path('my-recipes/', MyRecipeView.as_view(), name="view-user-recipe"),
    path('feed/', FeedAPIView.as_view(), name='feed'),

    path('yummly-autocomplete/', yummly_autocomplete, name='yummly_autocomplete'),
    path('yummly-search/', yummly_search, name='yummly_search'),
    path('yummly-feeds-list/', yummly_feeds_list, name='yummly_feeds_list'),
    path('category-feed/', category_feed, name='category_feed'),
    path('get-categories-list/', get_categories_list, name='get_categories_list'),
    path('get-list-similarities/', get_list_similarities, name='get_list_similarities'),
    path('get-time-based-recipes/', time_based_yummly_feeds, name='get_time_based_feed'),
]

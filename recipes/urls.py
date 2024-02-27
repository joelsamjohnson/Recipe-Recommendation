from django.urls import path
from . import views
from django.conf import settings

urlpatterns = [
    path('all_data/', views.all_data),
    path('recomm/', views.recommend_recipe),
    path('time_based/', views.time_based_recipes),
    path('recipes/', views.RecipeList.as_view(), name='recipe_list'),
    path('recipes/<int:pk>/', views.RecipeDetailView.as_view(), name='recipe_detail'),
    path('search/', views.RecipeSearchView.as_view(), name='recipe-search')

]
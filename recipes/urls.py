from django.urls import path
from .views import yummly_autocomplete, yummly_search, yummly_feeds_list, get_categories_list,\
                 get_list_similarities

urlpatterns = [
    path('yummly-autocomplete/', yummly_autocomplete, name='yummly_autocomplete'),
    path('yummly-search/', yummly_search, name='yummly_search'),
    path('yummly-feeds-list/', yummly_feeds_list, name='yummly_feeds_list'),
    path('get-categories-list/', get_categories_list, name='get_categories_list'),
    path('get-list-similarities/', get_list_similarities, name='get_list_similarities'),

]

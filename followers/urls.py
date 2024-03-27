from django.urls import path
from .views import *

app_name = "followers"

urlpatterns = [
    # path('find-followers', FindFollowersListView.as_view(), name="find-friends"),
    path('followers-list', ListFollowersAPIView.as_view(), name="followers-list"),
    path('follow/', FollowUserAPIView.as_view(), name='follow-user')
]

from django.urls import path
from . import views


urlpatterns = [
    path('getusers/',views.Register_user.as_view()),
    path('userlogin/',views.UserLoginAPIView.as_view()),
]

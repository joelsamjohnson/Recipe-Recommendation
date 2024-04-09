from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, ListCreateAPIView, RetrieveUpdateAPIView, UpdateAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from recipe.models import Recipe
from .models import Profile, Certificate
from recipe.serializers import RecipeSerializer
from .serializers import CertificateSerializer
from . import serializers

User = get_user_model()


class UserRegisterationAPIView(GenericAPIView):
    """
    An endpoint for the client to create a new User. 
    """
    permission_classes = (AllowAny,)
    serializer_class = serializers.UserRegisterationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = RefreshToken.for_user(user)
        data = serializer.data
        data['tokens'] = {
            'refresh': str(token),
            'access': str(token.access_token)
        }
        return Response(data, status=status.HTTP_201_CREATED)


class UserLoginAPIView(GenericAPIView):
    """
    An endpoint to authenticate existing users using their email and password.
    """
    permission_classes = (AllowAny,)
    serializer_class = serializers.UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        serializer = serializers.CustomUserSerializer(user)
        token = RefreshToken.for_user(user)
        data = serializer.data
        data['tokens'] = {
            'refresh': str(token),
            'access': str(token.access_token)
        }
        return Response(data, status=status.HTTP_200_OK)


class UserLogoutAPIView(GenericAPIView):
    """
    An endpoint to logout users.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserAPIView(RetrieveUpdateAPIView):
    """
    Get, Update user information
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.CustomUserSerializer

    def get_object(self):
        return self.request.user


class UserProfileAPIView(RetrieveUpdateAPIView):
    """
    Get, Update user profile
    """
    queryset = Profile.objects.all()
    serializer_class = serializers.ProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user.profile


class UserCertificateUploadAPIView(GenericAPIView):
    serializer_class = CertificateSerializer

    def post(self, request, *args, **kwargs):
        # Assume the user profile is linked to the user and identified by 'profile_id' in the request
        profile_id = request.data.get('profile')
        user_profile = Profile.objects.get(id=profile_id)

        # Optional: Check if the user is authorized to upload to this profile
        if request.user != user_profile.user:
            return Response({"status": 0,"message": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()  # Save the new certificate with the uploaded file
            return Response({"status": 1, "message": 'Certificate uploaded', "data": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"status": 0, "message": 'Certificate upload error', "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserVerifiedStatusAPIView(GenericAPIView):
    """
    Get user profile verified status
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            profile = Profile.objects.get(user=user)
            certificate = Certificate.objects.get(profile=profile)
            is_verified = certificate.verified
        except (Profile.DoesNotExist, Certificate.DoesNotExist):
            return Response({"error": "Profile or certificate not found.", "verified": False})

        return Response({"status": is_verified})


class UserAvatarAPIView(RetrieveUpdateAPIView):
    """
    Get, Update user avatar
    """
    queryset = Profile.objects.all()
    serializer_class = serializers.ProfileAvatarSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user.profile


class UserBookmarkAPIView(ListCreateAPIView):
    """
    Get, Create, Delete favorite recipe
    """
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticated,)
    profile = Profile.objects.all()

    def get_queryset(self):
        user = User.objects.get(id=self.kwargs['pk'])
        user_profile = get_object_or_404(self.profile, user=user)
        return user_profile.bookmarks.all()

    def post(self, request, pk):
        user = User.objects.get(id=pk)
        user_profile = get_object_or_404(self.profile, user=user)
        recipe = Recipe.objects.get(id=request.data['id'])
        if user_profile:
            user_profile.bookmarks.add(recipe)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = User.objects.get(id=pk)
        user_profile = get_object_or_404(self.profile, user=user)
        recipe = Recipe.objects.get(id=request.data['id'])
        if user_profile:
            user_profile.bookmarks.remove(recipe)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeAPIView(UpdateAPIView):
    """
    Change password view for authenticated user
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.PasswordChangeSerializer

    def get_object(self):
        return self.request.user


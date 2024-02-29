from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer, UserLoginSerializer
from .models import User

from django.contrib.auth import authenticate


class Register_user(APIView):

    def post(self, request):
        register_serializer = UserSerializer(data=request.data)
        if register_serializer.is_valid():
            register_serializer.save()
            return Response(register_serializer.data, status=status.HTTP_201_CREATED)
        return Response(register_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginAPIView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')

            user = authenticate(username=username, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                serialized_user = UserSerializer(user)
                return Response({
                    'user': serialized_user.data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'status': f"{user.username} logged in successfully",
                })
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

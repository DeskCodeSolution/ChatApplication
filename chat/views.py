from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .models import *
from rest_framework import status
from .serializers import *
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import re

class UserRegisterView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        try:
            # Trim whitespace from input fields
            email = request.data.get("email", "").strip()
            password = request.data.get("password", "").strip()
            name = request.data.get("name", "").strip()

            # Validate email format
            if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                return Response({
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Please enter a valid email address."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Validate password strength
            if not password or len(password) < 8:
                return Response({
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Password must be at least 8 characters long."
                }, status=status.HTTP_400_BAD_REQUEST)
            if not any(char.isdigit() for char in password):
                return Response({
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Password must contain at least one numeric character."
                }, status=status.HTTP_400_BAD_REQUEST)
            if not any(char.isupper() for char in password):
                return Response({
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Password must contain at least one uppercase letter."
                }, status=status.HTTP_400_BAD_REQUEST)
            if not any(char.islower() for char in password):
                return Response({
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Password must contain at least one lowercase letter."
                }, status=status.HTTP_400_BAD_REQUEST)
            if not any(char in "!@#$%^&*()-_=+[]{}|;:,.<>?/`~" for char in password):
                return Response({
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Password must contain at least one special character."
                }, status=status.HTTP_400_BAD_REQUEST)

            user = UserMaster.objects.filter(email=email).first()
            if user:
                return Response({
                    "status_code": status.HTTP_409_CONFLICT,
                    "message": "This email is already registered. Please log in or use a different email."
                }, status=status.HTTP_409_CONFLICT)

            modified_data = request.data.copy()
            modified_data['email'] = email
            modified_data['password'] = password
            modified_data['name'] = name

            serializer = UserRegistrationSerializer(data=modified_data)
            if not serializer.is_valid():
                return Response({
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Please enter a valid email address."
                }, status=status.HTTP_400_BAD_REQUEST)

            user = serializer.save()    
            user.save()

            return Response({
                "status_code": status.HTTP_201_CREATED,
                "message": "User Registered Successfully!",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"status_code": status.HTTP_500_INTERNAL_SERVER_ERROR, 'message': 'An error occurred.', 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from rest_framework import status
from .serializers import *
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import re



def index(request):
    print("running html")
    return render(request, "chat/index.html")

def room(request, room_name, id):
    return render(request, "chat/room.html", {"room_name": room_name, "id": id})

class UserRegisterView(APIView):

    def post(self, request):
        try:

            email = request.data.get("email").strip()
            password = request.data.get("password").strip()
            name = request.data.get("name").strip()


            if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                return Response({
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Please enter a valid email address."
                }, status=status.HTTP_400_BAD_REQUEST)


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
            print("modified_data", modified_data)
            modified_data['email'] = email
            modified_data['password'] = password
            modified_data['name'] = name

            serializer = UserRegistrationSerializer(data=modified_data)
            if not serializer.is_valid():
                return Response({
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Please enter a valid email address."
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()

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


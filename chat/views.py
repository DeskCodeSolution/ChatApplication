from django.shortcuts import render
from rest_framework.authentication import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
import json
from .models import *
from rest_framework import status
from .serializers import *
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import re
from django.shortcuts import redirect
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .utils import generate


def get_tokens_for_user(user):

    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


#html page ulrs


def register(request):
    return render(request, "chat/register.html")

def login(request):
    return render(request, "chat/login.html")

# def room(request, room_id, user_id):
#     return render(request, "chat/room.html", {"room_id":room_id, "user_id":user_id})

# def createroom(request, user_id):
#     return render(request, "chat/createroom.html", {"user_id":user_id})


#user registration
class UserRegisterView(APIView):

    @extend_schema(
    tags=['Authentications'],
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'email': {'type': 'string'},
                'password': {'type': 'string'},
                'name': {'type': 'string'},
                'image': {'type': 'string', 'format': 'binary', 'description': 'Profile image file'}
            },
            'required': ['email', 'password', 'name']
        }
    },
    responses={201: {"description": "User Registered Successfully"}, 409: {"description": "Email already exists"}},
    )

    def post(self, request):
        try:
            print(request.data)
            name = request.data.get("name")
            email = request.data.get("email")
            password = request.data.get("password")

            print("name, email, password", name, email, password)

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
            print("user", user)
            if user:
                return Response({
                    "status_code": status.HTTP_409_CONFLICT,
                    "message": "This email is already registered. Please log in or use a different email."
                }, status=status.HTTP_409_CONFLICT)

            modified_data = request.data.copy()
            modified_data['email'] = email
            modified_data['password'] = password
            modified_data['name'] = name
            print(modified_data)

            serializer = UserRegistrationSerializer(data=modified_data)
            print("55")
            if serializer.is_valid():
                print("1753")
                user = serializer.save()
                return Response({
                    "status_code": status.HTTP_201_CREATED,
                    "message": "User Registered Successfully!",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
                return Response({
                    "status_code": status.HTTP_201_CREATED,
                    "message": "User Registered Successfully!.",
                    "errors": serializer.data
                }, status=status.HTTP_400_BAD_REQUEST)
            print("333")
            print("88")

            return Response({
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "invalid data provided!.",
                "data": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"status_code": status.HTTP_500_INTERNAL_SERVER_ERROR, 'message': 'An error occurred.', 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
    tags=['Authentications']
    )
    def get(self, request):
        queryset = UserMaster.objects.all()
        serializers = UserRegistrationSerializer(queryset, many=True)
        return Response({
            "status": status.HTTP_200_OK,
            "data": serializers.data
        })

    @extend_schema(
    tags=['Authentications'],
      request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'image': {'type': 'string', 'format': 'binary', 'description': 'Profile image file'}
            },
            'required': ['image']
        }
    },
    )
    def patch(self, request):

        try:
            data = request.data
            print("data", data)
            id = request.user.id
            print("id", id)
            try:

                instance = UserMaster.objects.get(id = id)
                serializer = UserRegistrationSerializer(instance, data=request.data, partial = True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(
                        {
                            "status_code":status.HTTP_200_OK,
                            "msg":"user data updated successfully",
                        }
                    )
                return Response(
                    serializer.errors,
                    status=400
                )
            except UserMaster.DoesNotExist:
                return Response(
                    {
                     "status":status.HTTP_400_BAD_REQUEST,
                     "msg":"record not exists"
                    },
                    status.HTTP_404_NOT_FOUND

                )
        except Exception as e:
            return Response(
                {"status_code": status.HTTP_500_INTERNAL_SERVER_ERROR, 'message': 'An error occurred.', 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

#user login view
class LoginView(APIView):

    @extend_schema(
    tags=['Authentications'],
    request= LoginSerializer,
    responses={200: {"description": "Login successful"}},
    )
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        print("email, name", email, password)
        try:
            user = authenticate(request=request, email=email, password=password)
            if user:
                tokens = get_tokens_for_user(user)
                user_data = UserMaster.objects.get(email=email)

                return Response({
                    "status":200,
                    "message":"login successfully",
                    "user_id": user_data.id,
                    "username": user_data.name,
                    "token":tokens


                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "status": status.HTTP_401_UNAUTHORIZED,
                    "message": "Invalid email or password"
                }, status=status.HTTP_401_UNAUTHORIZED)

        except UserMaster.DoesNotExist:
            return Response({
                "status": status.HTTP_404_NOT_FOUND,
                "message": "User not found"
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


####user logout functionality######

class LogoutView(APIView):


    @extend_schema(
    tags=['Authentications'],
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'refresh_token': {'type': 'string'},
            },
        }
    },
    responses={200: {"description": "user logout successfully"}},
    )

    def post(self, request):
        try:
            auth_header = request.headers.get('Authorization', '')
            if auth_header and auth_header.startswith('Bearer '):
                access_token = auth_header.split(' ')[1]
                BlacklistedAccessToken.objects.create(token=access_token)
            refresh_token = request.data.get("refresh_token")

            if not refresh_token:
                return Response({
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Refresh token is required"
                }, status=status.HTTP_400_BAD_REQUEST)
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception as e:
                return Response({
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid token or token has expired",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "status_code": status.HTTP_200_OK,
                "message": "User logout Successfully"
            })
        except Exception as e:
            return Response({
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid token or token has expired",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

# room creation view with post request data:-
#room_id, user_id
class RoomDataView(APIView):

    @extend_schema(
    tags=['Rooms'],
    request=RoomDataViewSerializer,
    responses={201: {"description": "Room data created successfully"}},
    )
    def post(self, request):
        try:
            room_id = request.data.get("room_id")
            user_id = request.user.id
            print(room_id, user_id)

            if not room_id or not user_id:
                return Response({
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Room ID and user IDs are required"
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = UserMaster.objects.get(id=user_id)
                print("user", user)

                try:
                    existing_room = RoomManagement.objects.get(room_id=room_id)
                    if existing_room:
                            return Response({
                                "status_code": status.HTTP_409_CONFLICT,
                                "message": "User is already in this room"
                            }, status=status.HTTP_409_CONFLICT)

                except RoomManagement.DoesNotExist:
                    room = RoomManagement.objects.create(room_id=room_id, user=user)
                    print("room", room)

                return Response({
                    "status_code": status.HTTP_201_CREATED,
                    "message": "Room created and user added successfully"
                }, status=status.HTTP_201_CREATED)

            except UserMaster.DoesNotExist:
                return Response({
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "message": "One or more users not found"
                }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "An error occurred while creating the room",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        tags=['Rooms'])
    def get(self, request):
        try:
            # user_id = request.user.id
            user_id = 39
            room = RoomManagement.objects.filter(user__id=user_id)
            print("rooms", room)
            serializer = RoomDataViewSerializer(room, many=True)
            return Response({
                "data":serializer.data
            })

        except Exception as e:
            return Response({
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "An error occurred while creating the room",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#get chat history of the users
class ChatHistory(APIView):

    @extend_schema(
    tags=['Rooms']
    )
    def get(self, request):
        try:
            user_id = request.user.id
            print(user_id)
            try:
                queryset = RoomManagement.objects.filter(user_id = user_id)
                serializers = RoomHistorySerializer(queryset, many = True)
                return Response({
                    "status_code" : status.HTTP_200_OK,
                    "msg":"message history get successfully",
                    "data":serializers.data
                }, status.HTTP_200_OK)
            except RoomManagement.DoesNotExist:
                return Response({
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "message": "Room not found"
                }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Failed to retrieve chat history",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



  
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


def get_tokens_for_user(user):

    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def login(request):
    return render(request, "chat/login.html")

def room(request, room_name, id):
    return render(request, "chat/room.html", {"room_name": room_name, "id": id})

def createroom(request, user_name, user_id):
    return render(request, "chat/createroom.html", {"user_name":user_name, "user_id":user_id})

class UserRegisterView(APIView):

    @extend_schema(
    tags=['Authentications'],
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'email': {'type': 'string'},
                'password': {'type': 'string'},
                'name': {'type': 'string'}
            },
            'required': ['email', 'password', 'name']
        }
    },
    responses={201: {"description": "User Registered Successfully"}, 409: {"description": "Email already exists"}},
    )

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

    def get(self, request):

        user_id = request.user.id
        data = RoomManagement.objects.filter(users = user_id)
        user_list = []
        list2 = []
        res_data = []
        for data in data:
            room_users = data.users.all()
            for user in room_users:
                if user.id not in list2:
                    list2.append(user.id)
                    res_data.append({"id":user.id})
            user_list.append(data.roomId)

        filtered_list = []
        for d in res_data:
            if d['id'] != user_id:
                filtered_list.append(d)


        filtered_ids = [item['id'] for item in filtered_list]

        queryset = UserMaster.objects.exclude(id=user_id).exclude(id__in=filtered_ids)
        serializers = UserRegistrationSerializer(queryset, many=True)


        return Response({
            "status": status.HTTP_200_OK,
            "data": serializers.data
        })

class LoginView(APIView):

    @extend_schema(
    tags=['Authentications'],
    request= LoginSerializer,
    responses={200: {"description": "Login successful"}},
    )

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
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

class RoomDataView(APIView):

    @extend_schema(
    tags=['Rooms'],
    request=RoomDataViewSerializer,
    responses={201: {"description": "Room data created successfully"}},
    )

    def post(self, request):
        serializer = RoomDataViewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status_code": status.HTTP_201_CREATED,
                "message": "Room data created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status_code": status.HTTP_400_BAD_REQUEST,
            "message": "Invalid data",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



class LoadContentData(APIView):
    permission_classes = [IsAuthenticated,]

    def get(self, request):

        try:

            auth_header = request.headers.get('Authorization', '')
            if auth_header and auth_header.startswith('Bearer '):
                access_token = auth_header.split(' ')[1]

            user_id = request.user.id


            data = RoomManagement.objects.filter(users = user_id)
            room_Id_list = []
            list2 = []
            res_data = []
            for data in data:
                room_users = data.users.all()
                for user in room_users:
                    if user.id not in list2:
                        list2.append(user.id)

                        res_data.append({"id":user.id, "name":user.name, "roomId":data.roomId})

                room_Id_list.append(data.roomId)
            filtered_list = []

            for d in res_data:
                if d['id'] != user_id:

                  filtered_list.append(d)


            return Response({
                "status_code": status.HTTP_200_OK,
                "message": "Content data loaded successfully",
                "data": filtered_list,

            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Failed to load content data",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatHistory(APIView):

    def post(self, request):
        data = request.data
        print("data", data)
        return Response({"msg":"sucess"})



    def get(self, request):
        # user_id = request.user.id
        user_id = 2

        data = RoomManagement.objects.filter(users = user_id)
        print("data", data)
        return Response({"msg":"get data"})







class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

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
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid token or token has expired",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)










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


#html page ulrs

def login(request):
    return render(request, "chat/login.html")

def room(request, room_name, id):
    return render(request, "chat/room.html", {"room_name": room_name, "id": id})

def createroom(request, user_name, user_id):
    return render(request, "chat/createroom.html", {"user_name":user_name, "user_id":user_id})


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
                'phone_no':{'type':'string'},
            },
            'required': ['email', 'password', 'name', 'phone_no']
        }
    },
    responses={201: {"description": "User Registered Successfully"}, 409: {"description": "Email already exists"}},
    )

    def post(self, request):
        try:

            email = request.data.get("email", "").strip()
            password = request.data.get("password", "").strip()
            name = request.data.get("name", "").strip()
            phone_no = request.data.get("phone_no")



            if not phone_no:
                return Response({
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Phone number is required."
                }, status=status.HTTP_400_BAD_REQUEST)

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
            modified_data['phone_no'] = phone_no


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
        queryset = UserMaster.objects.all()
        serializers = UserRegistrationSerializer(queryset, many=True)
        return Response({
            "status": status.HTTP_200_OK,
            "data": serializers.data
        })

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


#room creation view with post request data:-
#roomname, users list, login user_id, selected user id
class RoomDataView(APIView):

    @extend_schema(
    tags=['Rooms'],
    request=RoomDataViewSerializer,
    responses={201: {"description": "Room data created successfully"}},
    )
    def post(self, request):
        try:
            room_id = request.data.get("roomId")
            user_ids = request.data.get("users")

            if not room_id or not user_ids:
                return Response({
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Room ID and user IDs are required"
                }, status=status.HTTP_400_BAD_REQUEST)


            room, created = RoomManagement.objects.get_or_create(roomId=room_id)

            try:
                for id in user_ids:
                    user = UserMaster.objects.get(id=id)
                    room.users.add(user)

                try:
                    phone_no = request.data.get('phone_no')
                    if phone_no:
                        contact = ContactList.objects.get(phone_no=phone_no)
                    else:
                        return Response({
                            "status_code": status.HTTP_400_BAD_REQUEST,
                            "message": "Phone number is required"
                        }, status=status.HTTP_400_BAD_REQUEST)
                except ContactList.DoesNotExist:
                    return Response({
                        "status_code": status.HTTP_404_NOT_FOUND,
                        "message": "Contact not found"
                    }, status=status.HTTP_404_NOT_FOUND)
                contact.room_id = room
                contact.save()

                single_room = RoomManagement.objects.get(roomId=room_id)
                username = single_room.users.all()


                for i in username:
                    if i.id != request.user.id:
                        id = i.id
                        single_room_user = UserMaster.objects.get(id = id)
                    if i.id == request.user.id:
                        ph = i.phone_no

                user = UserMaster.objects.get(id = request.user.id)
                name = user.name


                ContactList.objects.create(
                    name = name,
                    message = {},
                    room_id = room,
                    user_id = single_room_user,
                    phone_no = ph
                )

                return Response({
                    "status_code": status.HTTP_201_CREATED if created else status.HTTP_200_OK,
                    "message": "Room created and users added successfully" if created else "Users added to room successfully",
                    "data": {
                        "roomId": room.roomId,
                        "users": list(room.users.values('id', 'name'))
                    }
                }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

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


        except RoomManagement.DoesNotExist:
            pass

#data loaded get method
class LoadContentData(APIView):

    # permission_classes = [IsAuthenticated,]

    def get(self, request):
        try:
            user_id = request.user.id
            rooms = RoomManagement.objects.filter(users=user_id)

            room_ids = [room.id for room in rooms]
            user_list = []
            users = ContactList.objects.filter(room_id__in=room_ids).filter(user_id=request.user.id)

            for user in users:
                user_list.append({
                    'id': user.id,
                    'name': user.name,
                    'room_id': user.room_id.id
                })

            return Response({
                "status_code": status.HTTP_200_OK,
                "message": "Content data loaded successfully",
                "data": user_list,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Failed to load content data",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
            try:
                room_id = request.data.get('roomId')
                user_id = request.data.get('userId')
                if not room_id or not user_id:
                    return Response({
                        "status_code": status.HTTP_400_BAD_REQUEST,
                        "message": "Both roomId and userId are required"
                    }, status=status.HTTP_400_BAD_REQUEST)

                try:
                    user = ContactList.objects.get(id=user_id)
                    user.delete()
                    return Response({
                        "status_code":status.HTTP_200_OK,
                        "message":"user deleted",
                        "user":user.name
                    })

                except ContactList.DoesNotExist:
                    return Response({
                        "status_code": status.HTTP_404_NOT_FOUND,
                        "message": "User not found"
                    }, status=status.HTTP_404_NOT_FOUND)

            except Exception as e:
                return Response({
                    "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "message": "Failed to remove user from room",
                    "error": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#get chat history of the users
class ChatHistory(APIView):

    @extend_schema(
    tags=['chat'],
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'roomName': {'type': 'string'},
                'userId':{'type':'string'}
            },
        }
    },
    )

    def post(self, request):
        try:
            room_id = request.data.get("roomName")
            user_id = request.data.get("userId")
            if not room_id or not user_id:
                return Response({
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Room name and user ID are required"
                }, status=status.HTTP_400_BAD_REQUEST)

            queryset = ContactList.objects.filter(user_id = user_id).filter(room_id = room_id)


            userlist = []
            try:
                room = RoomManagement.objects.get(id=room_id)
                users = room.users.all()
                for user in users:
                    userlist.append({"id": user.id, "name": user.name})
            except RoomManagement.DoesNotExist:
                return Response({
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "message": "Room not found"
                }, status=status.HTTP_404_NOT_FOUND)

            for query in queryset:
                if query.message:
                    message_data = json.loads(query.message)

            return Response({
                "status_code": status.HTTP_200_OK,
                "message": "Chat history retrieved successfully",
                "data": message_data,
                "userlist":userlist
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Failed to retrieve chat history",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#####user contact list
class ContactListView(APIView):

        @extend_schema(
        tags=['Rooms'],
        request=ContactListSerializer,
        responses={201: {"description": "Room data created successfully"}},
        )

        def post(self, request):
            ph = request.data.get("phone_no")
            try:
                user = UserMaster.objects.get(phone_no = ph)
                if user:
                    serializer = ContactListSerializer(data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        return Response({
                            "status_code": status.HTTP_201_CREATED,
                            "message": "contact created successfully",
                            "data": serializer.data
                        }, status=status.HTTP_201_CREATED)

                    return Response({
                        "status_code": status.HTTP_400_BAD_REQUEST,
                        "message": "Invalid data",
                        "errors": serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
            except UserMaster.DoesNotExist:
                pass




        def get(self, request):
            try:
                user_id = request.user.id
                try:

                    user_id = request.user.id
                    rooms = RoomManagement.objects.filter(users=user_id)
                    room_ids = [room.id for room in rooms]

                    user_list_exclude = []
                    users = ContactList.objects.filter(room_id__in=room_ids).filter(user_id=request.user.id)

                    for user in users:
                         user_list_exclude.append(
                            user.id
                        )

                    user_list = []
                    users = ContactList.objects.exclude(id__in=user_list_exclude).filter(user_id=request.user)

                    for i in users:
                        user = UserMaster.objects.get(phone_no = i.phone_no)
                        selected_user_id = user.id
                        user_list.append({
                            "id":i.id,
                            "name":i.name,
                            "phone_no":i.phone_no,
                            "room_id":i.room_id.id if i.room_id else None,
                            "user_id":i.user_id.id if i.user_id else None,
                            "selected_user_id":selected_user_id
                        })

                    return Response({
                        "status":status.HTTP_200_OK,
                        "msg":"contact list get successfully",
                        "data":user_list,

                    })

                except RoomManagement.DoesNotExist:
                    return Response({
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "message": "not found",
                    "error": str(e)
                })

            except Exception as e:
                return Response({
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Failed to load content data",
                "error": str(e)
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


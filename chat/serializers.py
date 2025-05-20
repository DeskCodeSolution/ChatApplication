from rest_framework import serializers
from .models import *



class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    class Meta:
        model = UserMaster
        fields = ['id','email','password','name', 'phone_no']

    def create(self, validated_data):
        user = UserMaster.objects.create_user(
            password=validated_data['password'],
            email=validated_data['email'],
            name=validated_data['name'],
            phone_no = validated_data['phone_no']
        )

        return user

class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMaster
        fields = ['email','password']

class RoomDataViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = RoomManagement
        fields = ['roomId', 'users']

class ContactListSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContactList
        fields = ['id','name', 'user_id', 'room_id', 'message', 'phone_no']











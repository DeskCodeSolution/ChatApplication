from rest_framework import serializers
from .models import *



class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    class Meta:
        model = UserMaster
        fields = ['email','password','name']

    def create(self, validated_data):
        user = UserMaster.objects.create_user(
            password=validated_data['password'],
            email=validated_data['email'],
            name=validated_data['name']
        )

        return user

class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMaster
        fields = ['email','password']

class RoomDataViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = RoomManagement
        fields = ['roomId', 'message', 'users']







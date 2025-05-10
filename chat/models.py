from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
import time
import random

class CustomUserManager(BaseUserManager):

    def create_user(self, email, password, **extra_fields):

        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user


    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)

class UserMaster(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255,null=True,blank=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "email"

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class ChatManagement(models.Model):
    user_id = models.ForeignKey(UserMaster, on_delete=models.CASCADE)
    room_name = models.CharField(max_length=255)
    message = models.JSONField()
    created_at = models.TimeField(auto_now_add=True)


class RoomManagement(models.Model):
    roomId = models.CharField(max_length=255, unique=True)
    message = models.JSONField(
        default=dict,
        help_text="Must contain valid JSON data. Example: {'text': 'message content'}",
        error_messages={
            'invalid': 'Enter a valid JSON. Example: {"text": "message content"}',
        },
        null = True
    )
    users = models.ManyToManyField(UserMaster)

    def __str__(self):
        return str(self.roomId)
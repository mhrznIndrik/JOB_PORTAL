from datetime import datetime, timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .manager import CustomUserManager
from common.models import BaseModel
import uuid

class TokenType(models.TextChoices):
    PASSWORD_RESET = ("PASSWORD_RESET", )

class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = CustomUserManager()
    
class PendingUser(BaseModel):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    verification_code = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_valid(self) -> bool:
        lifetime_in_seconds = 20 * 60
        now = datetime.now(timezone.utc)
        
        timediff = now - self.created_at
        timediff = timediff.total_seconds()
        if timediff > lifetime_in_seconds:
            return False
        return True
    
class Token(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    token_type = models.CharField(max_length=100, choices = TokenType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user} {self.token}"
    
    def is_valid(self) -> bool:
        lifetime_in_seconds = 20 * 60 # 20 minutes
        now = datetime.now(timezone.utc)
        
        timediff = now - self.created_at
        timediff = timediff.total_seconds()
        if timediff > lifetime_in_seconds:
            return False
        return True
    
    def reset_user_password(self, raw_password: str):
        self.user: User
        self.user.set_password(raw_password)
        self.user.save()
    

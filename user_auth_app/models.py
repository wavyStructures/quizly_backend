from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """Manager for 'CustomUser'"""
    
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
           raise ValueError("The username field is required.")
        if not email:
            raise ValueError('Email must be set')

        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(username=username, email=email, password=password, **extra_fields)


class CustomUser(AbstractUser):
    """Quizly user model. Uses email as unique identifier."""

    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, max_length=255)
        
    objects = CustomUserManager()
    
    REQUIRED_FIELDS = ['email']


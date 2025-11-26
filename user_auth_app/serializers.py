from rest_framework import serializers
from django.conf import settings

from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'username']
        

class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for registering new users. Creating a new active user account.
    """

    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'confirmed_password', 'email']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'username': {'required': True}
        }

    def validate(self, data):
        if data["password"] != data["confirmed_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        validate_password(data["password"]) 
        return data

    def create(self, validated_data):
        validated_data.pop("confirmed_password")
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"]  
        )


class LoginSerializer(serializers.Serializer):
    """
    Serializer for authenticating users.
    """

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid username or password.")

        attrs["user"] = user
        return attrs

   
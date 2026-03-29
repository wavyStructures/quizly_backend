from rest_framework import serializers
from django.conf import settings

from django.contrib.auth import authenticate, get_user_model
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
        fields = ['username', 'email', 'password', 'confirmed_password']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'username': {'required': False}
        }

    def validate(self, data):
        if data["password"] != data["confirmed_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        validate_password(data["password"]) 
        return data

    def create(self, validated_data):
        validated_data.pop("confirmed_password")
        email = validated_data["email"]

        return User.objects.create_user(
            username=email,
            email=email,
            password=validated_data["password"]
        )


class LoginSerializer(serializers.Serializer):
    """
    Serializer for authenticating users.
    """
    email = serializers.EmailField(required=False)
    username = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email') or attrs.get('username')
        password = attrs.get('password')
        
        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        attrs["user"] = user
        return attrs

   
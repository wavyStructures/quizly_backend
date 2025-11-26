from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .serializers import RegistrationSerializer, LoginSerializer, UserSerializer

from .utils import (
    create_tokens_for_user,
    get_jwt_max_ages,
    set_auth_cookies,
)


User = get_user_model()


class RegisterView(APIView):
    """
    Handles user registration. Creates a new user.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        try:    
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            return Response(
                {"detail": "User created successfully!"},
                status=status.HTTP_201_CREATED,
            )
        
        except ValidationError:
            return Response({"detail": "Invalid data provided."}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    Handles user login. Validates user credentials. Issues refresh + access tokens. Stores tokens in secure cookies.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh_token, access_token = create_tokens_for_user(user)
        access_max_age, refresh_max_age = get_jwt_max_ages()
        
        response = Response(
            {
                "detail": "Login successfully!",
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )

        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/")

        set_auth_cookies(response, request, access_token, refresh_token, access_max_age, refresh_max_age)
        return response


class LogoutView(APIView):
    """
    Handles user logout. Invalidates refresh token. Deletes all authentication cookies.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response(
                {"detail": "Refresh token missing."},
                status=status.HTTP_400_BAD_REQUEST
            )

        token = RefreshToken(refresh_token)
        token.blacklist() 

        response = Response(
            {"detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."},
            status=status.HTTP_200_OK
        )

        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/")

        return response


class RefreshTokenView(APIView):
    """
    Issues a new access token using the refresh token from cookies. POST request required. 
    """
    permission_classes = [AllowAny]


    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response(
                {"detail": "Refresh token missing."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = refresh.access_token

            refresh.set_jti()
            new_refresh_token = str(refresh)

        except TokenError:
            return Response(
                {"detail": "Invalid refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        access_max_age, refresh_max_age = get_jwt_max_ages()
        
        response = Response(
            {"detail": "Token refreshed", "access": str(new_access_token)},
            status=status.HTTP_200_OK,
        )
        
        set_auth_cookies(
            response,
            request,
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            access_max_age=access_max_age,
            refresh_max_age=refresh_max_age
        )

        return response




from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
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
        serializer_class = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"detail": "User created successfully!"},
            status=status.HTTP_201_CREATED,
        )

        


# def _cookie_settings():
#     """
#     Returns secure cookie settings for JWT storage.
#     """
#     return dict(
#         httponly=True,
#         secure=getattr(settings, "SESSION_COOKIE_SECURE", True), 
#         samesite=getattr(settings, "SESSION_COOKIE_SAMESITE", "Lax"),
#     )


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
                "detail": "Login successful",
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )

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
            {"detail": "Logout successful! All tokens will be deleted. Refresh token is now invalid."},
            status=status.HTTP_200_OK
        )

        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/")
        response.delete_cookie("csrftoken", path="/")

        return response

    # except Exception as e:
    #     return Response({"error": str(e)}, status=500)


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
            new_access = refresh.access_token
        except TokenError:
            return Response(
                {"detail": "Invalid refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        access_max_age = int(
            getattr(settings, 'SIMPLE_JWT', {}) 
            .get('ACCESS_TOKEN_LIFETIME')
            .total_seconds()
        )
        
        resp = Response(
            {"detail": "Token refreshed", "access": str(new_access)},
            status=status.HTTP_200_OK,
        )
        
        resp.set_cookie(
            key="access_token",
            value=str(new_access),
            max_age=access_max_age,
            **_cookie_settings(),
        )

        return resp




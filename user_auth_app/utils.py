from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.middleware.csrf import get_token
from rest_framework_simplejwt.tokens import RefreshToken


def create_tokens_for_user(user):
    """Create and return (refresh_token_str, access_token_str) for a user."""
    
    refresh = RefreshToken.for_user(user)
    access = refresh.access_token
    return str(refresh), str(access)


def get_jwt_max_ages():
    """Return (access_max_age_seconds, refresh_max_age_seconds) or (None, None)
    if the corresponding SIMPLE_JWT settings are not present."""
    
    simple_jwt = getattr(settings, "SIMPLE_JWT", {})
    access_td = simple_jwt.get("ACCESS_TOKEN_LIFETIME")
    refresh_td = simple_jwt.get("REFRESH_TOKEN_LIFETIME")
    access_max_age = int(access_td.total_seconds()) if access_td is not None else None
    refresh_max_age = int(refresh_td.total_seconds()) if refresh_td is not None else None
    return access_max_age, refresh_max_age


def cookie_settings():
    """Common cookie flags used for auth cookies."""
    
    return {
    "httponly": True,
    "secure": getattr(settings, "SESSION_COOKIE_SECURE", True),
    "samesite": getattr(settings, "SESSION_COOKIE_SAMESITE", "Lax"),
    }


def set_auth_cookies(response, request, access_token, refresh_token, access_max_age=None, refresh_max_age=None):
    """
    Mutates the given DRF `Response` by setting access/refresh/csrf cookies and returns it.
    `access_max_age` / `refresh_max_age` may be None — in that case cookies are session cookies.
    """
    
    flags = cookie_settings()

    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=access_max_age,
        **flags,
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=refresh_max_age,
        **flags,
    )

    response.set_cookie(
        key="csrftoken",
        value=get_token(request),
        max_age=access_max_age,
        secure=getattr(settings, "SESSION_COOKIE_SECURE", True),
        samesite=getattr(settings, "SESSION_COOKIE_SAMESITE", "Lax"),
        httponly=False,
    )

    return response
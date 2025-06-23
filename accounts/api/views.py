from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import RegisterSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from config.utils import default_rate_limit

CustomUser = get_user_model()

@method_decorator(ratelimit(key='ip', rate='3/h', block=True), name='dispatch')
class RegisterView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_id="user_register",
        operation_description="Register a new user.",
        tags=["Authentication"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email", "password1", "password2"],
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="User email"),
                "password1": openapi.Schema(type=openapi.TYPE_STRING, description="User password"),
                "password2": openapi.Schema(type=openapi.TYPE_STRING, description="User password"),
            },
        ),
        responses={
            201: openapi.Response(
                description="User created",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(type=openapi.TYPE_STRING, example="User created")
                    }
                )
            ),
            400: "Bad Request"
        }
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "User created"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@default_rate_limit
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="user_logout",
        operation_description="Logout user and blacklist refresh token",
        tags=["Authentication"],
        security=[{'Bearer': []}],
        responses={
            200: openapi.Response(
                description="Logout successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(type=openapi.TYPE_STRING, example="Logout successful.")
                    }
                )
            ),
            400: openapi.Response(description="Refresh token required or invalid/expired."),
            401: openapi.Response(description="Unauthorized")
        }
    )
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout successful."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"detail": "Invalid or expired refresh token."},
                status=status.HTTP_400_BAD_REQUEST
            )


@method_decorator(ratelimit(key='ip', rate='3/h', block=True), name='dispatch')
class CustomTokenObtainPairView(TokenObtainPairView):
    @swagger_auto_schema(
        operation_id="user_login",
        operation_description="Login and obtain JWT access and refresh tokens.",
        tags=["Authentication"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email", "password"],
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="User email"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, description="User password"),
            },
        ),
        responses={
            200: openapi.Response(
                description="Tokens generated",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "access": openapi.Schema(type=openapi.TYPE_STRING),
                        "refresh": openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: openapi.Response(description="Bad request"),
            401: openapi.Response(description="Unauthorized"),
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


@default_rate_limit
class CustomTokenRefreshView(TokenRefreshView):
    @swagger_auto_schema(
        operation_id="refresh_access_token",
        operation_description="Refresh JWT access token.",
        tags=["Authentication"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["refresh"],
            properties={
                "refresh": openapi.Schema(type=openapi.TYPE_STRING, description="Refresh token"),
            },
        ),
        responses={
            200: openapi.Response(
                description="Access token refreshed",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "access": openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: openapi.Response(description="Bad request"),
            401: openapi.Response(description="Unauthorized"),
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

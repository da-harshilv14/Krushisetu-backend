from rest_framework import generics
from .models import User
from django.http import HttpResponse
from django.template.loader import render_to_string
from .serializers import UserSignupSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .otp_utils import send_otp_sms, verify_otp_sms
from .auth_utils import login_with_otp_success
from dotenv import load_dotenv, dotenv_values 
from django.conf import settings
import random
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import PasswordResetOTP  # a model to store OTP temporarily
import os
otp = ""


User = get_user_model()

@api_view(['POST'])
def forgot_password_send_otp(request):
    load_dotenv()
    email = request.data.get('email')
    if not email:
        return HttpResponse("Email is required", status=400)

    otp = str(random.randint(100000, 999999))
    subject = f"Email verification code: {otp}"
    message = f'Your OTP is {otp}, please do not share it with anyone'
    html_content = render_to_string("otp_email.html", {"otp": otp, "user_email": email})
    from_email = os.getenv('EMAIL_HOST_USER')
    recipient_list = [email]

    try:
        # check user exists
        user = User.objects.get(email_address=email)

        # store OTP in DB
        PasswordResetOTP.objects.update_or_create(
            user=user,
            defaults={"otp": otp}
        )

        send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=html_content)
        return HttpResponse("Email sent successfully!")
    except User.DoesNotExist:
        return HttpResponse("User not found.", status=404)
    except Exception as e:
        return HttpResponse(f"Error sending email: {e}", status=500)

@api_view(['POST'])
def forgot_password_verify_otp(request):
    email = request.data.get('email')
    otp = request.data.get('otp')

    if not email or not otp:
        return HttpResponse("Email and OTP required.", status=400)

    try:
        user = User.objects.get(email_address=email)
        otp_obj = PasswordResetOTP.objects.get(user=user)

        if otp_obj.otp != otp:
            return HttpResponse("Invalid OTP.", status=400)

        return HttpResponse("OTP verified successfully.")
    except User.DoesNotExist:
        return HttpResponse("User not found.", status=404)
    except PasswordResetOTP.DoesNotExist:
        return HttpResponse("No OTP found for this user.", status=400)
@api_view(['POST'])
def forgot_password_reset(request):
    email = request.data.get('email')
    new_password = request.data.get('new_password')

    if not email or not new_password:
        return Response({'error': 'Email and new password required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email_address=email)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    user.password = make_password(new_password)
    user.save()

    # cleanup OTPs for this user
    PasswordResetOTP.objects.filter(user=user).delete()

    return Response({'message': 'Password reset successful.'}, status=status.HTTP_200_OK)


class UserSignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer
    permission_classes = []  # anyone can sign up



from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    role = serializers.CharField(write_only=True)  # Accept role in request

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token["full_name"] = user.full_name
        token["email_address"] = user.email_address
        token["role"] = user.role
        return token

    def validate(self, attrs):
        # Get role from request
        role = attrs.pop('role', None)

        # First validate email/password
        data = super().validate(attrs)

        # Check role matches
        if role and self.user.role != role:
            raise serializers.ValidationError({"role": "Invalid role for this user."})

        # Add user info to response
        data.update({
            "user": {
                "id": self.user.id,
                "email": self.user.email_address,
                "full_name": self.user.full_name,
                "role": self.user.role
            }
        })

        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        data = response.data

        refresh = data.get("refresh")
        access = data.get("access")

        # Set HttpOnly cookies
        response.set_cookie(
            key="access_token",
            value=access,
            httponly=True,
            secure=True,   # set True in production
            samesite="Strict",
            max_age=300,    # 5 mins
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh,
            httponly=True,
            secure=True,
            samesite="Strict",
            max_age=7*24*60*60,  # 7 days
        )

        # Remove tokens from response body
        del response.data["access"]
        del response.data["refresh"]

        return response


class CookieTokenRefreshView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token is None:
            return Response({"error": "No refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(refresh_token)
            access = str(refresh.access_token)

            response = Response({"message": "Token refreshed"}, status=status.HTTP_200_OK)
            response.set_cookie(
                key="access_token",
                value=access,
                httponly=True,
                secure=False,
                samesite="Strict",
                max_age=300,   # 5 minutes
            )
            return response

        except Exception:
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

class LoginOtpView(APIView):
    def post(self, request):
        mobile_number = request.data.get("mobile_number")
        try:
            user = User.objects.get(mobile_number=mobile_number)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        otp = send_otp_sms(user)
        return Response({"message": "OTP sent", "user_id": user.id})

class VerifyOTPView(APIView):
    def post(self, request):
        user_id = request.data.get("user_id")
        token = request.data.get("otp")

        try:
            user = User.objects.get(id=user_id)
            if verify_otp_sms(user, token):
                return login_with_otp_success(user)
            else:
                return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        

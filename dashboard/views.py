from django.shortcuts import render
import sqlite3
from rest_framework import generics

from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from dotenv import load_dotenv, dotenv_values 
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
def information(request):
 conn = sqlite3.connect('db.sqlite3')
 cursor = conn.cursor()
 email = request.data.get('email')
 cursor.execute("SELECT * FROM db.sqlite3 WHERE email = ?", (email,))
 rows = cursor.fetchall()
 return Response({f'{rows}'}, status=status.HTTP_200_OK)

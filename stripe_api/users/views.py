from django.shortcuts import render
from django.conf import settings
import jwt
# Create your views here.
from rest_framework import generics, status
from .serializers import RegisterSerializer, LoginSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .models import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib import auth
import stripe
stripe.api_key = 'sk_test_51HY1nrHs3yuV19rz0uU2MOeuhDIuPxtbdwOo52mfvvCsfizFOcQxlcFfZGVUmUVZo83kcScZAHGVLvL1r1Xjh7B200jNIIKQFn'

class RegisterAPIView(generics.GenericAPIView):

    serializer_class = RegisterSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data

        user = CustomUser.objects.get(email=user_data['email'])

        token = RefreshToken.for_user(user).access_token

        current_site=get_current_site(request)

        relative_link = reverse("email-verify-create-custom-account")

        absurl = "http://"+str(current_site)+relative_link+"?token="+str(token)

        email_body = "Hi, Use link below to verify your email\n"+ absurl

        data = {'email_body': email_body, 'email': user.email, 'email_subject': "Verify your email"}

        Util.send_email(data)

        return Response(user_data, status=status.HTTP_201_CREATED)

class VerifyEmailAndCreateCustomAccountAPI(generics.GenericAPIView):

    token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])

    def get(self, request):
        token = request.GET.get("token")
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
            user = CustomUser.objects.get(id=payload["user_id"])
            if not user.is_verified:
                user.is_verified = True
                
                #create custom account
                account = stripe.Account.create(
                country=user.user_country,
                type='custom',
                email=user.email,
                requested_capabilities=['card_payments', 'transfers'],
                )

                user.user_custom_account_id = account.id 

                user.save()
            return Response(account, status = status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identfier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_404_NOT_FOUND)
        except jwt.exceptions.DecodeError as identfier:
            return Response({'error': 'invalid token. Invalid Link'}, status=status.HTTP_404_NOT_FOUND)

class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)







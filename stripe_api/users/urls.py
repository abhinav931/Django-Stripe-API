from django.urls import path
from .import views

urlpatterns=[
    path('register', views.RegisterAPIView.as_view(), name="register"),
    path('email-verify-create-custom-account', views.VerifyEmailAndCreateCustomAccountAPI.as_view(), name="email-verify-create-custom-account"),
    path('login', views.LoginAPIView.as_view(), name="login"),
]
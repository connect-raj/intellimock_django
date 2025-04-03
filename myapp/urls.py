from django.urls import path
from .views import *

urlpatterns = [
    path("login", logIn, name="login"),
    path("signup/", signUp, name="signUp"),
    path("delete/<id>", delUser, name="delUser"),
    path("user/<id>", userView, name="userView"),
    path("resume/", resumeView, name="resumeView"),
]
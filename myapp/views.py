from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
import uuid

# Create your views here.
@csrf_exempt
def logIn(request):
    
    if request.method == 'POST':
        username = 'admin'
        password = 'admin'

        if username == 'admin' and password == 'admin':
            return HttpResponse('Success')

    return HttpResponse('error')


def signUp(request):

    if request.method == 'POST':
        userFullName = request.POST.get('userName')
        userEmail = request.POST.get('userEmail')
        userPassword = request.POST.get('userPassword')
        userType = request.POST.get('userType')

        userInstance = User.objects.create(userId = uuid.uuid4(),userFullName=userFullName, userEmail=userEmail, userPassword=userPassword, userType=userType)
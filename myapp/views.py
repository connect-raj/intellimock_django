import json
import jwt
import uuid
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from .models import *  
from .serializers import *  

@api_view(["POST"])
def signUp(request):
    try: 
        if request.method == 'POST':
            data = json.loads(request.body)
            userFullName = data.get('userFullName')
            userEmail = data.get('userEmail')
            userPassword = data.get('userPassword')
            userType = data.get('userType')

            # Validate email and password (optional)
            if not userEmail or not userPassword:
                return JsonResponse({'msg': 'Email and password are required'}, status=400)

            # Hash the password before saving
            hashed_password = make_password(userPassword)

            # Check if the user already exists (to prevent duplicate registrations)
            if UserData.objects.filter(userEmail=userEmail).exists():
                return JsonResponse({'msg': 'Email already exists'}, status=400)

            # Create the new user
            userInstance = UserData.objects.create(
                userId=str(uuid.uuid4()),
                userFullName=userFullName,
                userEmail=userEmail,
                userPassword=hashed_password,
                userType=userType
            )

            userInstance.save()

            # Generate JWT token after user creation
            token = generate_jwt(userInstance)

            # Return response with userId as a string
            return JsonResponse({'msg': 'User created successfully', 'token': token, 'userId': str(userInstance.userId)}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"message": "Server Error"}, status=500)
    except Exception as e:
        return JsonResponse({"message": str(e)}, status=500)

# Helper function to create JWT
def generate_jwt(user):
    payload = {
        'user_id': user.userId,
        'email': user.userEmail,
        'exp': datetime.utcnow() + timedelta(hours=24),  # 24 hours expiration
        'iat': datetime.utcnow()  # Issued at
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

@csrf_exempt
@api_view(['POST'])
def logIn(request):
    try:
        data = json.loads(request.body)
        userEmail = data.get('userEmail')
        userPassword = data.get('userPassword')

        if not userEmail or not userPassword:
            return JsonResponse({'msg': 'Email and password are required'}, status=400)

        # Check if user exists
        try:
            userInstance = UserData.objects.get(userEmail=userEmail)
        except UserData.DoesNotExist:
            return JsonResponse({'msg': 'No Such Email Found'}, status=400)

        # Verify the password using check_password method
        if not check_password(userPassword, userInstance.userPassword):
            return JsonResponse({'msg': 'Invalid username or password'}, status=400)

        # Generate JWT token on successful login
        token = generate_jwt(userInstance)
        return JsonResponse({'msg': 'Logged in successfully', 'token': token}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"message": "Server Error"}, status=500)

@api_view(['DELETE'])
def delUser(request, id):
    try:
        print(id)
        userInstance = UserData.objects.get(userId=id)
        userInstance.delete()
        return JsonResponse({'msg': 'User deleted successfully'}, status=200)
    except Exception as e:
        return JsonResponse({'msg': 'An error occurred while deleting'},status=400)
    

@api_view(['GET'])
def userView(request, id):
    
    if request.method == 'GET':
        try:
            userInstance = UserData.objects.get(userId=id)
            serializer = userSerializer(userInstance)
            return JsonResponse(serializer.data, status=200)
        except Exception as e:
            return JsonResponse({'msg': 'An error occurred while retrieving user data'}, status=400)
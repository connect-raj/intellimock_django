import json
import jwt
import uuid
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, render
from .models import *  
from .serializers import *  
from .utils.resume import *
from .utils.pdf_uploader import *

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
        'userId': user.userId,
        'email': user.userEmail,
        'exp': datetime.utcnow() + timedelta(hours=24),  # 24 hours expiration
        'iat': datetime.utcnow()  # Issued at
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def verify_jwt(token):
    try:
        # Decode the token using the secret key and the algorithm
        decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return decoded_payload
    except jwt.ExpiredSignatureError:
        return JsonResponse({'msg': 'Token has expired'}, status=401)
    except jwt.InvalidTokenError:
        return JsonResponse({'msg': 'Invalid token'}, status=401)


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

    token = request.headers.get('token').split(' ')[1]
    user_data = verify_jwt(token)
    
    if user_data:
        try:
            userInstance = UserData.objects.get(userId=id)
            userInstance.delete()
            return JsonResponse({'msg': 'User deleted successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'msg': 'An error occurred while deleting'},status=400)
    else:
        return JsonResponse({'msg': 'Invalid token'}, status=401)
    


@api_view(['GET','POST'])
def userView(request, id):

    token = request.headers.get('token').split(' ')[1]
    user_data = verify_jwt(token)
    print(user_data)
    if user_data['userId']!= id:
        return JsonResponse({'msg': 'Invalid token'}, status=401)

    if request.method == 'GET':
        try:
            userInstance = UserData.objects.get(userId=id)
            serializer = userSerializer(userInstance)
            return JsonResponse(serializer.data, status=200)
        except Exception as e:
            return JsonResponse({'msg': 'An error occurred while retrieving user data'}, status=400)
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            userInstance = get_object_or_404(UserData, userId=id)
            serializer = userSerializer(userInstance, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'msg': "User updated successfully", 'data': serializer.data}, status=200)
            return JsonResponse(serializer.errors, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'msg': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'msg': str(e)}, status=500)
        

@api_view(['GET','POST'])
def resumeView(request):

    token = request.headers.get('token').split(' ')[1]
    user_data = verify_jwt(token=token)
    
    if request.method == "GET":
        try:
            resumeInstance = resumeSerializer(Resume.objects.get(userId=user_data["userId"]))
            if resumeInstance.is_valid():
                return JsonResponse({'id': user_data["userId"]}, status=200)
        except Resume.DoesNotExist:
            return JsonResponse({'msg': 'No resume found for this user'}, status=404)
    
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            file = request.FILES.get('pdf_file')
            if not file: 
                return JsonResponse({'msg': 'No File Provided'}, status=400)
            
            ## Logic for uploading files to S3 or Cloudinary and getting the URL
            cloud_url = upload_pdf(file)
            # skills = 
            
        except Exception as e:
            return JsonResponse({'msg': str(e)}, status=500)
        

def test(request):

    if request.method == "POST":
        pdf_file = request.FILES.get('pdf_file')

        print(extract_skills_from_uploaded_pdf(pdf_file))

    
    return render(request, "test.html")
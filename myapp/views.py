import json
import jwt
import uuid
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import UserData, Resume, Interview, mockInterview as MockInterview, IntSchedule, Applicants
from .serializers import userSerializer, resumeSerializer, interviewSerializer, mockIntSerializer
from .utils.resume import extractSkills
from .utils.pdf_uploader import upload_pdf

def generate_jwt(user):
    payload = {
        'userId': str(user.userId),
        'email': user.userEmail,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def verify_jwt_from_cookie(request):
    """Get and verify JWT from cookie"""
    token = request.COOKIES.get('jwt_token')
    if not token:
        return None
    
    try:
        decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return decoded_payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@api_view(["POST"])
@csrf_exempt
def signUp(request):
    try: 
        data = json.loads(request.body)
        userFullName = data.get('userFullName')
        userEmail = data.get('userEmail')
        userPassword = data.get('userPassword')
        userType = data.get('userType', 'user')

        if not userEmail or not userPassword:
            return JsonResponse({'msg': 'Email and password are required'}, status=400)

        if UserData.objects.filter(userEmail=userEmail).exists():
            return JsonResponse({'msg': 'Email already exists'}, status=400)

        hashed_password = make_password(userPassword)
        userInstance = UserData.objects.create(
            userId=str(uuid.uuid4()),
            userFullName=userFullName,
            userEmail=userEmail,
            userPassword=hashed_password,
            userType=userType
        )

        token = generate_jwt(userInstance)
        
        # Create response with user data
        response = JsonResponse({
            'msg': 'User created successfully', 
            'userId': str(userInstance.userId)
        }, status=201)
        
        # Set JWT as secure HTTP-only cookie
        response.set_cookie(
            key='jwt_token',
            value=token,
            httponly=True,
            samesite='Lax',
            secure=settings.DEBUG is False,  # True in production (HTTPS)
            max_age=86400,  # 24 hours in seconds
            path='/'
        )
        
        return response

    except json.JSONDecodeError:
        return JsonResponse({"msg": "Invalid JSON format"}, status=400)
    except Exception as e:
        return JsonResponse({"msg": str(e)}, status=500)

@api_view(['POST'])
@csrf_exempt
def logIn(request):
    try:
        data = json.loads(request.body)
        userEmail = data.get('userEmail')
        userPassword = data.get('userPassword')
        
        if not userEmail or not userPassword:
            return JsonResponse({'msg': 'Email and password are required'}, status=400)

        try:
            userInstance = UserData.objects.get(userEmail=userEmail)
        except UserData.DoesNotExist:
            return JsonResponse({'msg': 'No Such Email Found'}, status=400)

        if not check_password(userPassword, userInstance.userPassword):
            return JsonResponse({'msg': 'Invalid username or password'}, status=400)

        token = generate_jwt(userInstance)
        
        # Create response with user data
        response = JsonResponse({
            'msg': 'Logged in successfully',
            'userId': str(userInstance.userId)
        }, status=200)
        
        # Set JWT as secure HTTP-only cookie
        response.set_cookie(
            key='jwt_token',
            value=token,
            httponly=True,
            samesite='Lax',
            secure=settings.DEBUG is False,  # True in production (HTTPS)
            max_age=86400,  # 24 hours in seconds
            path='/'
        )
        
        return response

    except json.JSONDecodeError:
        return JsonResponse({"msg": "Invalid JSON format"}, status=400)
    except Exception as e:
        return JsonResponse({"msg": str(e)}, status=500)

@api_view(['POST'])
def logOut(request):
    """Logout endpoint to clear the JWT cookie"""
    response = JsonResponse({'msg': 'Logged out successfully'}, status=200)
    response.delete_cookie('jwt_token')
    return response

@api_view(['DELETE'])
def delUser(request, id):
    try:
        # Verify user from cookie instead of Authorization header
        user_data = verify_jwt_from_cookie(request)
        
        if not user_data:
            return JsonResponse({'msg': 'Authentication required'}, status=401)
        
        userInstance = UserData.objects.get(userId=id)
        userInstance.delete()
        
        # Create response and clear cookie
        response = JsonResponse({'msg': 'User deleted successfully'}, status=200)
        response.delete_cookie('jwt_token')
        return response
        
    except UserData.DoesNotExist:
        return JsonResponse({'msg': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'msg': str(e)}, status=500)

@api_view(['GET', 'POST'])
def userView(request, id):
    try:
        # Verify user from cookie
        user_data = verify_jwt_from_cookie(request)
        
        if not user_data or user_data.get('userId') != id:
            return JsonResponse({'msg': 'Invalid token or unauthorized access'}, status=401)

        if request.method == 'GET':
            userInstance = get_object_or_404(UserData, userId=id)
            serializer = userSerializer(userInstance)
            return JsonResponse(serializer.data, status=200)
        
        elif request.method == 'POST':
            data = json.loads(request.body)
            userInstance = get_object_or_404(UserData, userId=id)
            serializer = userSerializer(userInstance, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({
                    'msg': "User updated successfully", 
                    'data': serializer.data
                }, status=200)
            return JsonResponse(serializer.errors, status=400)
    
    except json.JSONDecodeError:
        return JsonResponse({'msg': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'msg': str(e)}, status=500)

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@csrf_exempt
def resumeView(request):
    try:
        # Verify user from cookie instead of Authorization header
        user_data = verify_jwt_from_cookie(request)
        
        if not user_data:
            return JsonResponse({'msg': 'Authentication required'}, status=401)
        
        user_id = user_data["userId"]
        
        if request.method == "GET":
            try:
                resumeInstance = Resume.objects.get(userId=user_id)
                serializer = resumeSerializer(resumeInstance)
                return JsonResponse(serializer.data, status=200)
            except Resume.DoesNotExist:
                return JsonResponse({'msg': 'No resume found for this user'}, status=404)
        
        elif request.method == "POST":
            file = request.FILES.get('pdf_file')
            if not file: 
                return JsonResponse({'msg': 'No File Provided'}, status=400)
            
            fileName = str(uuid.uuid4())
            cloud_url = upload_pdf(file, fileName)
            skills = extractSkills(file)
            experience = request.POST.get("experience", 0)
            
            # Ensure experience is an integer
            try:
                experience = int(experience)
            except (ValueError, TypeError):
                return JsonResponse({'msg': 'Experience must be a number'}, status=400)
                
            try:
                user = UserData.objects.get(userId=user_id)
                resumeInstance = Resume.objects.create(
                    resumeId=fileName,
                    userId=user,
                    cloudUrl=cloud_url,
                    skills=skills,
                    experience=experience
                )
                
                serializer = resumeSerializer(resumeInstance)
                return JsonResponse({
                    'msg': "Resume upload successful",
                    'data': serializer.data
                }, status=201)
            except UserData.DoesNotExist:
                return JsonResponse({'msg': 'User not found'}, status=404)
            
        elif request.method == "PUT":
            data = json.loads(request.body)
            try:
                user = UserData.objects.get(userId=user_id)
                resumeInstance = Resume.objects.get(userId=user)
                
                serializer = resumeSerializer(resumeInstance, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return JsonResponse({
                        'msg': 'Updated resume successfully',
                        'data': serializer.data
                    }, status=200)
                return JsonResponse(serializer.errors, status=400)
            except UserData.DoesNotExist:
                return JsonResponse({'msg': 'User not found'}, status=404)
            except Resume.DoesNotExist:
                return JsonResponse({'msg': 'Resume not found for this user'}, status=404)
            
        elif request.method == "DELETE":
            try:
                user = UserData.objects.get(userId=user_id)
                resumeInstance = Resume.objects.get(userId=user)
                resumeInstance.delete()
                return JsonResponse({'msg': 'Resume deleted successfully'}, status=200)
            except UserData.DoesNotExist:
                return JsonResponse({'msg': 'User not found'}, status=404)
            except Resume.DoesNotExist:
                return JsonResponse({'msg': 'Resume not found'}, status=404)
    
    except json.JSONDecodeError:
        return JsonResponse({'msg': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'msg': str(e)}, status=500)

@api_view(['GET', 'POST', 'DELETE'])
@csrf_exempt
def interviewView(request, intId=None):
    try:
        # Verify user from cookie
        user_data = verify_jwt_from_cookie(request)
        
        if not user_data:
            return JsonResponse({'msg': 'Authentication required'}, status=401)
        
        user_id = user_data["userId"]
        
        if request.method == "GET":
            try:
                user = UserData.objects.get(userId=user_id)
                if intId:
                    interviewInstance = get_object_or_404(Interview, interviewId=intId)
                    if str(interviewInstance.userId.userId) != user_id:
                        return JsonResponse({'msg': 'Unauthorized access to this interview'}, status=403)
                    serializer = interviewSerializer(interviewInstance)
                    return JsonResponse(serializer.data, status=200)
                else:
                    interviews = Interview.objects.filter(userId=user)
                    serializer = interviewSerializer(interviews, many=True)
                    return JsonResponse({'interviews': serializer.data}, safe=False, status=200)
            except UserData.DoesNotExist:
                return JsonResponse({'msg': 'User not found'}, status=404)
        
        elif request.method == "POST":
            try:
                data = json.loads(request.body)
                user = UserData.objects.get(userId=user_id)
                
                interviewInstance = Interview.objects.create(
                    interviewId=str(uuid.uuid4()),
                    userId=user,
                    skill=data.get('skill', ''),
                    level=data.get('level', '')
                )
                
                serializer = interviewSerializer(interviewInstance)
                return JsonResponse({
                    'msg': 'Interview scheduled successfully', 
                    'data': serializer.data
                }, status=201)
            except UserData.DoesNotExist:
                return JsonResponse({'msg': 'User not found'}, status=404)
        
        elif request.method == "DELETE":
            try:
                if not intId:
                    return JsonResponse({'msg': 'Interview ID is required'}, status=400)
                    
                interviewInstance = get_object_or_404(Interview, interviewId=intId)
                
                # Check if the user owns this interview
                if str(interviewInstance.userId.userId) != user_id:
                    return JsonResponse({'msg': 'Unauthorized action'}, status=403)
                    
                interviewInstance.delete()
                return JsonResponse({'msg': 'Interview deleted successfully'}, status=200)
            except Interview.DoesNotExist:
                return JsonResponse({'msg': 'Interview not found'}, status=404)
    
    except json.JSONDecodeError:
        return JsonResponse({'msg': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'msg': str(e)}, status=500)

@api_view(['GET', 'POST', 'DELETE'])
@csrf_exempt
def mockInterviewView(request, intId=None):
    try:
        # Verify user from cookie
        user_data = verify_jwt_from_cookie(request)
        
        if not user_data:
            return JsonResponse({'msg': 'Authentication required'}, status=401)
        
        user_id = user_data["userId"]
        
        if request.method == "GET":
            try:
                if intId:
                    mockIntInstance = get_object_or_404(MockInterview, mockInterviewId=intId)
                    # Check if user has access to this interview's parent interview
                    if str(mockIntInstance.interviewId.userId.userId) != user_id:
                        return JsonResponse({'msg': 'Unauthorized access'}, status=403)
                    
                    serializer = mockIntSerializer(mockIntInstance)
                    return JsonResponse(serializer.data, status=200)
                else:
                    # Get all interviews for this user
                    user = UserData.objects.get(userId=user_id)
                    interviews = Interview.objects.filter(userId=user)
                    
                    # Get all mock interviews for these interviews
                    mockInterviews = []
                    for interview in interviews:
                        mocks = MockInterview.objects.filter(interviewId=interview)
                        if mocks.exists():
                            mockInterviews.extend(mocks)
                    
                    serializer = mockIntSerializer(mockInterviews, many=True)
                    return JsonResponse({'mockInterviews': serializer.data}, safe=False, status=200)
            except UserData.DoesNotExist:
                return JsonResponse({'msg': 'User not found'}, status=404)
        
        elif request.method == "POST":
            try:
                data = json.loads(request.body)
                interview_id = data.get('interviewId')
                if not interview_id:
                    return JsonResponse({'msg': 'Interview ID is required'}, status=400)
                
                interviewInstance = get_object_or_404(Interview, interviewId=interview_id)
                
                # Check if user has access to this interview
                if str(interviewInstance.userId.userId) != user_id:
                    return JsonResponse({'msg': 'Unauthorized action'}, status=403)
                
                feedback = data.get('feedBack', {})
                if not isinstance(feedback, dict):
                    return JsonResponse({'msg': 'Feedback must be a JSON object'}, status=400)
                
                mockIntInstance = MockInterview.objects.create(
                    mockInterviewId=str(uuid.uuid4()),
                    interviewId=interviewInstance,
                    feedBack=feedback
                )
                
                serializer = mockIntSerializer(mockIntInstance)
                return JsonResponse({
                    'msg': 'Mock interview created successfully', 
                    'data': serializer.data
                }, status=201)
            except Interview.DoesNotExist:
                return JsonResponse({'msg': 'Interview not found'}, status=404)
        
        elif request.method == "DELETE":
            try:
                if not intId:
                    return JsonResponse({'msg': 'Mock Interview ID is required'}, status=400)
                
                mockIntInstance = get_object_or_404(MockInterview, mockInterviewId=intId)
                
                # Check if the user owns the parent interview of this mock interview
                if str(mockIntInstance.interviewId.userId.userId) != user_id:
                    return JsonResponse({'msg': 'Unauthorized action'}, status=403)
                    
                mockIntInstance.delete()
                return JsonResponse({'msg': 'Mock interview deleted successfully'}, status=200)
            except MockInterview.DoesNotExist:
                return JsonResponse({'msg': 'Mock interview not found'}, status=404)
    
    except json.JSONDecodeError:
        return JsonResponse({'msg': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'msg': str(e)}, status=500)

@api_view(['GET'])
def applicantInterviewSchedule(request, applicantId=None):
    try:
        # Verify user from cookie
        user_data = verify_jwt_from_cookie(request)
        
        if not user_data:
            return JsonResponse({'msg': 'Authentication required'}, status=401)
        
        user_id = user_data["userId"]
        
        # If applicantId is not provided, get the applicant for this user
        if not applicantId:
            try:
                applicant = Applicants.objects.get(userId=user_id)
                applicantId = applicant.applicantId
            except Applicants.DoesNotExist:
                return JsonResponse({'msg': 'No applicant profile found for this user'}, status=404)
        
        # Check if the user owns this applicant profile or is authorized to view it
        try:
            applicant = Applicants.objects.get(applicantId=applicantId)
            if str(applicant.userId.userId) != user_id:
                return JsonResponse({'msg': 'Unauthorized access to this applicant profile'}, status=403)
                
            # Get interview schedules for this applicant
            try:
                schedules = IntSchedule.objects.filter(applicantId=applicant)
                return JsonResponse({
                    'schedules': [
                        {
                            'scheduleId': schedule.scheduleId,
                            'intData': schedule.intData
                        } for schedule in schedules
                    ]
                }, status=200)
            except Exception as e:
                return JsonResponse({'msg': f'Error retrieving interview schedules: {str(e)}'}, status=500)
                
        except Applicants.DoesNotExist:
            return JsonResponse({'msg': 'Applicant not found'}, status=404)
        
    except Exception as e:
        return JsonResponse({'msg': str(e)}, status=500)

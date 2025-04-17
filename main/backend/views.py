import jwt
import uuid
import datetime
from main import settings
from django.http import HttpResponse, JsonResponse
from .models import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.utils import timezone
import json
from .decorators import jwt_required

# Constants
JWT_SECRET = settings.SECRET_KEY  # Change this in production
JWT_ALGORITHM = 'HS256'

# Helper Functions
def apiResponseHandler(data, message, status):
    return Response({
        'success': status<400,
        'status': status,
        'msg': message,
        'data': data or None,
    }, status=status)

def generate_jwt_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def get_user_from_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        raise ValidationError('Token has expired')
    except jwt.InvalidTokenError:
        raise ValidationError('Invalid token')

# Create your views here.
def home(request):
    return HttpResponse('<h1>Intellimock is running... 🚀</h1>')

@csrf_exempt
def userLogin(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            
            user = UserData.objects.get(userEmail=email)
            if check_password(password, user.userPassword):
                token = generate_jwt_token(user.userId)
                response = JsonResponse({
                    'message': 'Login successful',
                    'token': token,
                    'user': {
                        'id': user.userId,
                        'name': user.userFullName,
                        'email': user.userEmail,
                        'type': user.userType
                    }
                })
                response.set_cookie('jwt', token, httponly=True)
                return response
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
        except UserData.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def userRegister(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = UserData(
                userId=str(uuid.uuid4()),
                userFullName=data['name'],
                userEmail=data['email'],
                userPassword=make_password(data['password']),
                userType=data.get('type', 'user')
            )
            user.save()
            return JsonResponse({'message': 'User registered successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@jwt_required
def userProfile(request):
    if request.method == 'GET':
        try:
            user_id = request.user_id
            user = UserData.objects.get(userId=user_id)
            return JsonResponse({
                'id': user.userId,
                'name': user.userFullName,
                'email': user.userEmail,
                'type': user.userType
            })
        except UserData.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    elif request.method == 'PUT':
        try:
            user_id = request.user_id
            data = json.loads(request.body)
            user = UserData.objects.get(userId=user_id)
            
            if 'name' in data:
                user.userFullName = data['name']
            if 'email' in data:
                user.userEmail = data['email']
            
            user.save()
            return JsonResponse({'message': 'Profile updated successfully'})
        except UserData.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@jwt_required
def changePassword(request):
    if request.method == 'POST':
        try:
            user_id = request.user_id
            data = json.loads(request.body)
            user = UserData.objects.get(userId=user_id)
            
            if check_password(data['oldPassword'], user.userPassword):
                user.userPassword = make_password(data['newPassword'])
                user.save()
                return JsonResponse({'message': 'Password changed successfully'})
            return JsonResponse({'error': 'Invalid current password'}, status=401)
        except UserData.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@jwt_required
def getQuestions(request):
    if request.method == 'GET':
        try:
            questions = practiceQuestion.objects.all()
            return JsonResponse({
                'questions': [{
                    'id': q.questionId,
                    'question': q.question,
                    'type': q.Type,
                    'skill': q.skill,
                    'level': q.level
                } for q in questions]
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@jwt_required
def getQuestionById(request, id):
    if request.method == 'GET':
        try:
            question = practiceQuestion.objects.get(questionId=id)
            return JsonResponse({
                'id': question.questionId,
                'question': question.question,
                'type': question.Type,
                'skill': question.skill,
                'level': question.level
            })
        except practiceQuestion.DoesNotExist:
            return JsonResponse({'error': 'Question not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@jwt_required
def createQuestion(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question = practiceQuestion(
                questionId=str(uuid.uuid4()),
                question=data['question'],
                Type=data['type'],
                skill=data['skill'],
                level=data['level']
            )
            question.save()
            return JsonResponse({'message': 'Question created successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@jwt_required
def updateQuestion(request, id):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            question = practiceQuestion.objects.get(questionId=id)
            
            if 'question' in data:
                question.question = data['question']
            if 'type' in data:
                question.Type = data['type']
            if 'skill' in data:
                question.skill = data['skill']
            if 'level' in data:
                question.level = data['level']
            
            question.save()
            return JsonResponse({'message': 'Question updated successfully'})
        except practiceQuestion.DoesNotExist:
            return JsonResponse({'error': 'Question not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@jwt_required
def deleteQuestion(request, id):
    if request.method == 'DELETE':
        try:
            question = practiceQuestion.objects.get(questionId=id)
            question.delete()
            return JsonResponse({'message': 'Question deleted successfully'})
        except practiceQuestion.DoesNotExist:
            return JsonResponse({'error': 'Question not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@jwt_required
def filterQuestions(request):
    if request.method == 'GET':
        try:
            type = request.GET.get('type')
            skill = request.GET.get('skill')
            level = request.GET.get('level')
            
            questions = practiceQuestion.objects.all()
            if type:
                questions = questions.filter(Type=type)
            if skill:
                questions = questions.filter(skill=skill)
            if level:
                questions = questions.filter(level=level)
                
            return JsonResponse({
                'questions': [{
                    'id': q.questionId,
                    'question': q.question,
                    'type': q.Type,
                    'skill': q.skill,
                    'level': q.level
                } for q in questions]
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@jwt_required
def getInterviews(request):
    if request.method == 'GET':
        try:
            interviews = Interview.objects.all()
            return JsonResponse({
                'interviews': [{
                    'id': i.interviewId,
                    'title': i.title,
                    'description': i.description,
                    'duration': i.duration,
                    'status': i.status
                } for i in interviews]
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@jwt_required
def getInterviewById(request, id):
    if request.method == 'GET':
        try:
            interview = Interview.objects.get(interviewId=id)
            return JsonResponse({
                'id': interview.interviewId,
                'title': interview.title,
                'description': interview.description,
                'duration': interview.duration,
                'status': interview.status
            })
        except Interview.DoesNotExist:
            return JsonResponse({'error': 'Interview not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@jwt_required
def createInterview(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            interview = Interview(
                interviewId=str(uuid.uuid4()),
                title=data['title'],
                description=data['description'],
                duration=data['duration'],
                status='scheduled'
            )
            interview.save()
            return JsonResponse({'message': 'Interview created successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@jwt_required
def updateInterview(request, id):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            interview = Interview.objects.get(interviewId=id)
            
            if 'title' in data:
                interview.title = data['title']
            if 'description' in data:
                interview.description = data['description']
            if 'duration' in data:
                interview.duration = data['duration']
            if 'status' in data:
                interview.status = data['status']
            
            interview.save()
            return JsonResponse({'message': 'Interview updated successfully'})
        except Interview.DoesNotExist:
            return JsonResponse({'error': 'Interview not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@jwt_required
def deleteInterview(request, id):
    if request.method == 'DELETE':
        try:
            interview = Interview.objects.get(interviewId=id)
            interview.delete()
            return JsonResponse({'message': 'Interview deleted successfully'})
        except Interview.DoesNotExist:
            return JsonResponse({'error': 'Interview not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@jwt_required
def scheduleInterview(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            interview = Interview.objects.get(interviewId=data['interviewId'])
            interview.scheduled_time = data['scheduledTime']
            interview.status = 'scheduled'
            interview.save()
            return JsonResponse({'message': 'Interview scheduled successfully'})
        except Interview.DoesNotExist:
            return JsonResponse({'error': 'Interview not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@jwt_required
def submitInterviewFeedback(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            interview = Interview.objects.get(interviewId=id)
            interview.feedback = data['feedback']
            interview.status = 'completed'
            interview.save()
            return JsonResponse({'message': 'Feedback submitted successfully'})
        except Interview.DoesNotExist:
            return JsonResponse({'error': 'Interview not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@jwt_required
def getMockInterviews(request):
    if request.method == 'GET':
        try:
            mock_interviews = mockInterview.objects.all()
            return JsonResponse({
                'mock_interviews': [{
                    'id': m.mockInterviewId,
                    'title': m.title,
                    'description': m.description,
                    'duration': m.duration,
                    'status': m.status
                } for m in mock_interviews]
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@jwt_required
def getMockInterviewById(request, id):
    if request.method == 'GET':
        try:
            mock_interview = mockInterview.objects.get(mockInterviewId=id)
            return JsonResponse({
                'id': mock_interview.mockInterviewId,
                'title': mock_interview.title,
                'description': mock_interview.description,
                'duration': mock_interview.duration,
                'status': mock_interview.status
            })
        except mockInterview.DoesNotExist:
            return JsonResponse({'error': 'Mock interview not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@jwt_required
def createMockInterview(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mock_interview = mockInterview(
                mockInterviewId=str(uuid.uuid4()),
                title=data['title'],
                description=data['description'],
                duration=data['duration'],
                status='created'
            )
            mock_interview.save()
            return JsonResponse({'message': 'Mock interview created successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@jwt_required
def updateMockInterview(request, id):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            mock_interview = mockInterview.objects.get(mockInterviewId=id)
            
            if 'title' in data:
                mock_interview.title = data['title']
            if 'description' in data:
                mock_interview.description = data['description']
            if 'duration' in data:
                mock_interview.duration = data['duration']
            if 'status' in data:
                mock_interview.status = data['status']
            
            mock_interview.save()
            return JsonResponse({'message': 'Mock interview updated successfully'})
        except mockInterview.DoesNotExist:
            return JsonResponse({'error': 'Mock interview not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@jwt_required
def deleteMockInterview(request, id):
    if request.method == 'DELETE':
        try:
            mock_interview = mockInterview.objects.get(mockInterviewId=id)
            mock_interview.delete()
            return JsonResponse({'message': 'Mock interview deleted successfully'})
        except mockInterview.DoesNotExist:
            return JsonResponse({'error': 'Mock interview not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@jwt_required
def startMockInterview(request, id):
    if request.method == 'POST':
        try:
            mock_interview = mockInterview.objects.get(mockInterviewId=id)
            mock_interview.status = 'in_progress'
            mock_interview.start_time = timezone.now()
            mock_interview.save()
            return JsonResponse({'message': 'Mock interview started successfully'})
        except mockInterview.DoesNotExist:
            return JsonResponse({'error': 'Mock interview not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@jwt_required
def submitMockInterview(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mock_interview = mockInterview.objects.get(mockInterviewId=id)
            mock_interview.answers = data['answers']
            mock_interview.status = 'completed'
            mock_interview.end_time = timezone.now()
            mock_interview.save()
            return JsonResponse({'message': 'Mock interview submitted successfully'})
        except mockInterview.DoesNotExist:
            return JsonResponse({'error': 'Mock interview not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@jwt_required
def getCodeInterviews(request):
    if request.method == 'GET':
        try:
            code_interviews = codeInterview.objects.all()
            return JsonResponse({
                'code_interviews': [{
                    'id': c.codeInterviewId,
                    'language': c.language,
                    'time': c.time,
                    'question': c.question,
                    'code': c.code,
                    'output': c.output,
                    'feedback': c.feedBack
                } for c in code_interviews]
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@jwt_required
def getCodeInterviewById(request, id):
    if request.method == 'GET':
        try:
            code_interview = codeInterview.objects.get(codeInterviewId=id)
            return JsonResponse({
                'id': code_interview.codeInterviewId,
                'language': code_interview.language,
                'time': code_interview.time,
                'question': code_interview.question,
                'code': code_interview.code,
                'output': code_interview.output,
                'feedback': code_interview.feedBack
            })
        except codeInterview.DoesNotExist:
            return JsonResponse({'error': 'Code interview not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@jwt_required
def createCodeInterview(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code_interview = codeInterview(
                codeInterviewId=str(uuid.uuid4()),
                language=data['language'],
                time=data['time'],
                question=data['question'],
                code='',
                output='',
                feedBack=''
            )
            code_interview.save()
            return JsonResponse({'message': 'Code interview created successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@jwt_required
def updateCodeInterview(request, id):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            code_interview = codeInterview.objects.get(codeInterviewId=id)
            
            if 'language' in data:
                code_interview.language = data['language']
            if 'time' in data:
                code_interview.time = data['time']
            if 'question' in data:
                code_interview.question = data['question']
            if 'code' in data:
                code_interview.code = data['code']
            if 'output' in data:
                code_interview.output = data['output']
            if 'feedback' in data:
                code_interview.feedBack = data['feedback']
            
            code_interview.save()
            return JsonResponse({'message': 'Code interview updated successfully'})
        except codeInterview.DoesNotExist:
            return JsonResponse({'error': 'Code interview not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@jwt_required
def deleteCodeInterview(request, id):
    if request.method == 'DELETE':
        try:
            code_interview = codeInterview.objects.get(codeInterviewId=id)
            code_interview.delete()
            return JsonResponse({'message': 'Code interview deleted successfully'})
        except codeInterview.DoesNotExist:
            return JsonResponse({'error': 'Code interview not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@jwt_required
def startCodeInterview(request, id):
    if request.method == 'POST':
        try:
            code_interview = codeInterview.objects.get(codeInterviewId=id)
            code_interview.start_time = timezone.now()
            code_interview.save()
            return JsonResponse({'message': 'Code interview started successfully'})
        except codeInterview.DoesNotExist:
            return JsonResponse({'error': 'Code interview not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@jwt_required
def submitCodeInterview(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code_interview = codeInterview.objects.get(codeInterviewId=id)
            code_interview.code = data['code']
            code_interview.output = data['output']
            code_interview.feedBack = data['feedback']
            code_interview.end_time = timezone.now()
            code_interview.save()
            return JsonResponse({'message': 'Code interview submitted successfully'})
        except codeInterview.DoesNotExist:
            return JsonResponse({'error': 'Code interview not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@jwt_required
def getUserAnalytics(request):
    if request.method == 'GET':
        try:
            user_id = request.user_id
            # Implement user analytics logic here
            return JsonResponse({
                'total_interviews': 0,
                'completed_interviews': 0,
                'average_score': 0,
                'strengths': [],
                'weaknesses': []
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@jwt_required
def getInterviewAnalytics(request):
    if request.method == 'GET':
        try:
            # Implement interview analytics logic here
            return JsonResponse({
                'total_interviews': 0,
                'average_duration': 0,
                'success_rate': 0,
                'common_feedback': []
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@jwt_required
def uploadResume(request):
    if request.method == 'POST':
        try:
            if 'resume' not in request.FILES:
                return JsonResponse({'error': 'No file uploaded'}, status=400)
            
            resume_file = request.FILES['resume']
            # Implement resume upload logic here
            return JsonResponse({'message': 'Resume uploaded successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@jwt_required
def searchQuestions(request):
    if request.method == 'GET':
        try:
            query = request.GET.get('q', '')
            questions = practiceQuestion.objects.filter(question__icontains=query)
            return JsonResponse({
                'questions': [{
                    'id': q.questionId,
                    'question': q.question,
                    'type': q.Type,
                    'skill': q.skill,
                    'level': q.level
                } for q in questions]
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def userAuthStatus(request):
    if request.method == 'GET':
        try:
            token = request.COOKIES.get('jwt')
            if not token:
                return JsonResponse({'error': 'No token provided'}, status=401)
            
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_id = payload['user_id']
            user = UserData.objects.get(userId=user_id)
            
            return JsonResponse({
                'authenticated': True,
                'user': {
                    'id': user.userId,
                    'name': user.userFullName,
                    'email': user.userEmail,
                    'type': user.userType
                }
            })
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token has expired'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)
        except UserData.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def userLogout(request):
    if request.method == 'POST':
        response = JsonResponse({'message': 'Logout successful'})
        response.delete_cookie('jwt')
        return response


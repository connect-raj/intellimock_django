from django.urls import path
from .views import *

urlpatterns = [
    # User Management
    path('user/login/', userLogin),
    path('user/register/', userRegister),
    path('user/auth/status/', userAuthStatus),
    path('user/logout/', userLogout),
    path('user/profile/', userProfile),
    path('user/change-password/', changePassword),

    # Practice Questions
    path('questions/', getQuestions),
    path('question/<str:id>/', getQuestionById),
    path('questions/create/', createQuestion),
    path('questions/update/<str:id>/', updateQuestion),
    path('questions/delete/<str:id>/', deleteQuestion),
    path('questions/filter/', filterQuestions),

    # Interview Management
    path('interviews/', getInterviews),
    path('interview/<str:id>/', getInterviewById),
    path('interviews/create/', createInterview),
    path('interviews/update/<str:id>/', updateInterview),
    path('interviews/delete/<str:id>/', deleteInterview),
    path('interviews/schedule/', scheduleInterview),
    path('interviews/feedback/<str:id>/', submitInterviewFeedback),

    # Mock Interviews
    path('mock-interviews/', getMockInterviews),
    path('mock-interview/<str:id>/', getMockInterviewById),
    path('mock-interviews/create/', createMockInterview),
    path('mock-interviews/update/<str:id>/', updateMockInterview),
    path('mock-interviews/delete/<str:id>/', deleteMockInterview),
    path('mock-interviews/start/<str:id>/', startMockInterview),
    path('mock-interviews/submit/<str:id>/', submitMockInterview),

    # Code Interviews
    path('code-interviews/', getCodeInterviews),
    path('code-interview/<str:id>/', getCodeInterviewById),
    path('code-interviews/create/', createCodeInterview),
    path('code-interviews/update/<str:id>/', updateCodeInterview),
    path('code-interviews/delete/<str:id>/', deleteCodeInterview),
    path('code-interviews/start/<str:id>/', startCodeInterview),
    path('code-interviews/submit/<str:id>/', submitCodeInterview),

    # Analytics
    path('analytics/user/', getUserAnalytics),
    path('analytics/interviews/', getInterviewAnalytics),

    # File Uploads
    path('upload/resume/', uploadResume),

    # Search
    path('search/questions/', searchQuestions),
]
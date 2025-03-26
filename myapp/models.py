from django.db import models

# Create your models here.
class UserData(models.Model):
    userId = models.CharField(max_length=40, primary_key=True)
    userFullName = models.CharField(max_length=40, null=False)
    userEmail = models.EmailField(max_length=255, null=False)
    userPassword = models.CharField(max_length=18, null=False)
    userType = models.CharField(max_length=20, null=False, default='user')
    createdAt = models.DateTimeField(auto_now_add=True)

class Resume(models.Model):
    resumeId = models.CharField(max_length=40, primary_key=True)
    userId = models.ForeignKey(UserData, on_delete=models.CASCADE)
    cloudUrl = models.URLField(blank=True, null=True)
    skills = models.JSONField()
    experience = models.IntegerField(null=False)
    timestamp = models.DateTimeField(auto_now_add=True)

class Interview(models.Model):
    interviewId = models.CharField(max_length=40, primary_key=True)
    userId = models.ForeignKey(UserData, on_delete=models.CASCADE)
    skill = models.CharField(max_length=20)
    level = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)

class mockInterview(models.Model):
    mockInterviewId = models.CharField(max_length=40, primary_key=True)
    interviewId = models.ForeignKey(Interview, on_delete=models.CASCADE)
    feedBack = models.JSONField()
    timeStamp = models.DateTimeField(auto_now_add=True)


class codeInterview(models.Model):
    codeInterviewId = models.CharField(max_length=40, primary_key=True)
    interviewId = models.ForeignKey(Interview, on_delete=models.CASCADE)
    language = models.CharField(max_length=30)
    time = models.CharField(max_length=50)
    question = models.CharField(max_length = 1000)
    code = models.TextField()
    output = models.CharField(max_length = 1000)
    feedBack = models.CharField(max_length = 1000)
    timeStamp = models.DateTimeField(auto_now_add=True)
    
class practiceQuestion(models.Model):
    questionId = models.CharField(max_length = 40, primary_key=True)
    question= models.CharField(max_length=100)
    Type = models.CharField(max_length=100)
    skill= models.CharField(max_length=100)
    level = models.CharField(max_length=100)

class comments(models.Model):
    commentId = models.CharField(max_length = 40, primary_key=True)
    questionId = models.ForeignKey(practiceQuestion,max_length= 30, on_delete=models.CASCADE)
    userId = models.ForeignKey(UserData,max_length= 30, on_delete=models.CASCADE)
    userFullName = models.CharField(max_length=50)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Company(models.Model):
    companyId = models.CharField(max_length = 40, primary_key=True)
    companyName = models.CharField(max_length=100)
    companyEmail = models.EmailField()
    companyNumber = models.IntegerField()
    companyWebsite = models.URLField()
    companyAbout = models.TextField()
    companyAddress = models.CharField(max_length=200)

class JobRole(models.Model):
    jobRoleId = models.CharField(max_length = 40, primary_key=True)
    companyId = models.ForeignKey(Company, on_delete=models.CASCADE)
    jobTitle = models.CharField(max_length = 50)
    jobDescription = models.TextField()
    jobOpeningAvailable = models.IntegerField()
    jobConstraints = models.JSONField()
    jobExpireTime = models.IntegerField()

class Applicants(models.Model):
    applicantId = models.CharField(max_length = 40, primary_key=True)
    userId = models.ForeignKey(UserData, on_delete = models.CASCADE)
    userName = models.CharField(max_length = 30)
    userEmail = models.EmailField()
    skills = models.TextField()
    experience = models.IntegerField()


class IntSchedule(models.Model):
    scheduleId = models.CharField(max_length = 40, primary_key=True)
    applicantId = models.ForeignKey(Applicants, on_delete = models.CASCADE)
    intData = models.JSONField()
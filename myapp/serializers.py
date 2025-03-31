from rest_framework.serializers import ModelSerializer
from .models import *

class userSerializer(ModelSerializer):

    class Meta:
        model = UserData
        fields = "__all__"

class resumeSerializer(ModelSerializer):

    class Meta:
        model = Resume
        fields = "__all__"

class interviewSerializer(ModelSerializer):

    class Meta:
        model = Interview
        fields = "__all__"

class mockIntSerializer(ModelSerializer):

    class Meta:
        model = mockInterview
        fields = "__all__"

class codeIntSerializer(ModelSerializer):

    class Meta:
        model = codeInterview
        fields = "__all__"

class pracQuesSerializer(ModelSerializer):

    class Meta:
        model = practiceQuestion
        fields = "__all__"

class commentsSerializer(ModelSerializer):

    class Meta:
        model = comments
        fields = "__all__"

class companySerializer(ModelSerializer):

    class Meta:
        model = Company
        fields = "__all__"

class jobRoleSerializer(ModelSerializer):

    class Meta:
        model = JobRole
        fields = "__all__"

class applicantsSerializer(ModelSerializer):

    class Meta:
        model = Applicants
        fields = "__all__"
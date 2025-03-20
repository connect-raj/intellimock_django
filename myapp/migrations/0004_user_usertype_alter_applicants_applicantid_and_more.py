# Generated by Django 5.1.7 on 2025-03-20 18:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0003_alter_company_companynumber"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="userType",
            field=models.CharField(default="user", max_length=20),
        ),
        migrations.AlterField(
            model_name="applicants",
            name="applicantId",
            field=models.CharField(max_length=40, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="codeinterview",
            name="codeInterviewId",
            field=models.CharField(max_length=40, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="comments",
            name="commentId",
            field=models.CharField(max_length=40, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="company",
            name="companyId",
            field=models.CharField(max_length=40, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="interview",
            name="interviewId",
            field=models.CharField(max_length=40, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="intschedule",
            name="scheduleId",
            field=models.CharField(max_length=40, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="jobrole",
            name="jobRoleId",
            field=models.CharField(max_length=40, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="mockinterview",
            name="mockInterviewId",
            field=models.CharField(max_length=40, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="practicequestion",
            name="questionId",
            field=models.CharField(max_length=40, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="resume",
            name="resumeId",
            field=models.CharField(max_length=40, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="user",
            name="userId",
            field=models.CharField(max_length=40, primary_key=True, serialize=False),
        ),
    ]

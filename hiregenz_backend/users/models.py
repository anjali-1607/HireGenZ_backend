from django.db import models
from django.utils.timezone import now, timedelta
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
    ROLE_CHOICES = (
        ('recruiter', 'Recruiter'),
        ('candidate', 'Candidate'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.email


class Recruiter(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recruiter_profile'
    )
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    company_name = models.CharField(max_length=255)
    website_url = models.URLField()
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_expiration = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.company_name

    def generate_otp(self):
        from random import randint
        self.otp = f"{randint(100000, 999999)}"  # Generate a 6-digit OTP
        self.otp_expiration = now() + timedelta(minutes=10)  # OTP valid for 10 minutes
        self.save()


class Candidate(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='candidate_profile'
    )
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    skills = models.TextField(null=True, blank=True)  # Store skills as a comma-separated string
    resume_text = models.TextField(null=True, blank=True)  # Raw text extracted from resume
    certifications = models.TextField(null=True, blank=True)
    education = models.TextField(null=True, blank=True)
    work_experience = models.TextField(null=True, blank=True)
    total_work_experience = models.FloatField(null=True, blank=True, help_text="Total work experience in years, stored as a floating-point value.")
    professional_summary = models.TextField(null=True, blank=True)
    resume_file = models.CharField(max_length=512, null=True, blank=True)  # URL of the resume stored in S3
    otp = models.CharField(max_length=6, null=True, blank=True)  # OTP for verification
    is_verified = models.BooleanField(default=False)  # Verification status

    def __str__(self):
        return self.name or "Unnamed Candidate"


class CandidatePreference(models.Model):
    EMPLOYMENT_TYPE_CHOICES = [
        ('FULL_TIME', 'Full Time'),
        ('PART_TIME', 'Part Time'),
        ('FREELANCE', 'Freelance'),
        ('INTERNSHIP', 'Internship'),
        ('CONTRACT', 'Contract'),
    ]

    JOB_TYPE_CHOICES = [
        ('REMOTE', 'Remote'),
        ('HYBRID', 'Hybrid'),
        ('WFO', 'WFO'),         
    ]

    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE, related_name='preference')
    expected_salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    expected_salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    preferred_locations = models.JSONField(max_length=255, blank=True, null=True, default=list)  # List of preferred locations
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES, null=True, blank=True)
    employment_type = models.CharField(max_length=50, choices=EMPLOYMENT_TYPE_CHOICES, null=True, blank=True)  # Full-time, Part-time

    def __str__(self):
        return f"Preferences for {self.candidate.name or 'Unnamed Candidate'}"

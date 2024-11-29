from django.db import models

class Recruiter(models.Model):
    email = models.EmailField(unique=True)
    company_name = models.CharField(max_length=255)
    website_url = models.URLField()
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.company_name

class Candidate(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    skills = models.TextField(null=True, blank=True)  # Store skills as a comma-separated string
    resume_text = models.TextField(null=True, blank=True)  # Raw text extracted from resume
    certifications = models.TextField(null=True, blank=True)
    education = models.TextField(null=True, blank=True)
    work_experience = models.TextField(null=True, blank=True)
    professional_summary = models.TextField(null=True, blank=True)
    resume_file = models.FileField(upload_to="resumes/", null=True, blank=True)
    otp = models.CharField(max_length=6, null=True, blank=True)  # OTP for verification
    is_verified = models.BooleanField(default=False)  # Verification status

    def __str__(self):
        return self.name or "Unnamed Candidate"


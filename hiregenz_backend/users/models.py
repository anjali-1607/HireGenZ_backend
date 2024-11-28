from django.db import models

class Recruiter(models.Model):
    email = models.EmailField(unique=True)
    company_name = models.CharField(max_length=255)
    website_url = models.URLField()
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.company_name

class Candidate(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    resume = models.FileField(upload_to='resumes/')
    ats_score = models.FloatField(default=0.0)
    preferences = models.JSONField(default=dict)  # {location, salary, job_type}

    def __str__(self):
        return self.name

from django.db import models
from users.models import Recruiter

class JobPost(models.Model):
    recruiter = models.ForeignKey(Recruiter, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    experience = models.PositiveIntegerField()
    min_ctc = models.PositiveIntegerField()
    max_ctc = models.PositiveIntegerField()
    location = models.CharField(max_length=255)
    education = models.CharField(max_length=255)
    key_skills = models.JSONField()
    job_type = models.CharField(max_length=50)  # WFH, Hybrid, etc.
    employment_type = models.CharField(max_length=50)  # Full-time, Part-time
    industry_type = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    candidates_needed = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

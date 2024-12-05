import uuid
from django.db import models
from users.models import Candidate, Recruiter

class Test(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='tests')
    recruiter = models.ForeignKey(Recruiter, on_delete=models.CASCADE, related_name='tests')
    job_description = models.TextField()
    questions = models.JSONField()  # Store generated questions
    candidate_answers = models.JSONField(null=True, blank=True)  # Store candidate's submitted answers
    score = models.IntegerField(null=True, blank=True)  # Candidate's score
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    test_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)  # Unique test token
  
  
    def __str__(self):
        return f"Test for {self.candidate.name} by {self.recruiter.company_name}"

from django.db import models
from users.models import Candidate
from jobs.models import JobPost

class Match(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    job_post = models.ForeignKey(JobPost, on_delete=models.CASCADE)
    match_score = models.FloatField()  # Score between 0-100

    def __str__(self):
        return f"{self.candidate.name} - {self.job_post.title}: {self.match_score}%"
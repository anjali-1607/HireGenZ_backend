from django.db import models
from users.models import Candidate
from jobs.models import JobPost

class Application(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    job_post = models.ForeignKey(JobPost, on_delete=models.CASCADE)
    is_shortlisted = models.BooleanField(default=False)
    test_score = models.FloatField(null=True, blank=True)
    test_time_taken = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.candidate.name} applied to {self.job_post.title}"

from django.db import models
from applications.models import Application

class TestQuestion(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    question = models.TextField()
    options = models.JSONField()  # Example: {"A": "Option 1", "B": "Option 2"}
    correct_option = models.CharField(max_length=1)  # Example: "A"

    def __str__(self):
        return self.question

class TestResult(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE)
    score = models.FloatField()
    time_taken = models.FloatField()

    def __str__(self):
        return f"Result for {self.application.candidate.name}"

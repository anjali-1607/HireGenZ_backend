from django.urls import path
from .views import TestQuestionView, TestResultView

urlpatterns = [
    path('questions/', TestQuestionView.as_view(), name='test-questions'),
    path('results/', TestResultView.as_view(), name='test-results'),
]

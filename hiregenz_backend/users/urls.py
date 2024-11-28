from django.urls import path
from .views import RecruiterView, CandidateView

urlpatterns = [
    path('recruiter/', RecruiterView.as_view()),
    path('candidate/', CandidateView.as_view()),
]

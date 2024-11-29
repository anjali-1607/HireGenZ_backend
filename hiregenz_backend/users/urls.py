from django.urls import path
from .views import RecruiterView, ResumeUploadView, VerifyEmailView

urlpatterns = [
    path('recruiter/', RecruiterView.as_view()),
    # path('candidate/', CandidateView.as_view()),
    path("upload-resume/", ResumeUploadView.as_view(), name="upload-resume"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
]

from django.urls import path
from .views import ResumeUploadView, VerifyEmailView, RecruiterRegistrationView, OTPVerificationView

urlpatterns = [
    # path('candidate/', CandidateView.as_view()),
    path("upload-resume/", ResumeUploadView.as_view(), name="upload-resume"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
     path('register-recruiter/', RecruiterRegistrationView.as_view(), name='register_recruiter'),
    path('verify-otp/', OTPVerificationView.as_view(), name='verify_otp'),
]

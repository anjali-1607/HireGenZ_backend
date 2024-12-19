from django.urls import path
from .views import ResumeAnalysisView

urlpatterns = [
    path('', ResumeAnalysisView.as_view(), name='resume-analysis'),
]

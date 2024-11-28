from django.urls import path
from .views import MatchingView

urlpatterns = [
    path('match/<int:job_id>/', MatchingView.as_view(), name='match-candidates'),
]

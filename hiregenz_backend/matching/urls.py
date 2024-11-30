from django.urls import path
from .views import  MatchCandidatesView

urlpatterns = [
     path('match-candidates/<int:job_id>/', MatchCandidatesView.as_view(), name='match_candidates'),
]

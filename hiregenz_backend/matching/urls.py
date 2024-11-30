from django.urls import path
from .views import GetMatchedCandidatesView, MatchCandidatesView

urlpatterns = [
    path('match/<int:job_id>/', GetMatchedCandidatesView.as_view(), name='get-matched-candidates'),
     path('match-candidates/<int:job_id>/', MatchCandidatesView.as_view(), name='match_candidates'),
]

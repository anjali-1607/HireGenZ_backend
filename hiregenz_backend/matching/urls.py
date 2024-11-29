from django.urls import path
from .views import GetMatchedCandidatesView

urlpatterns = [
    path('match/<int:job_id>/', GetMatchedCandidatesView.as_view(), name='get-matched-candidates'),
]

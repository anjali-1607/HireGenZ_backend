from django.urls import path
from .views import RankStudentsByJobView,SendTestLinksToShortlistedView, RetrieveTestQuestionsView, SubmitTestAnswersView

urlpatterns = [
    path('send-links/<int:job_id>/', SendTestLinksToShortlistedView.as_view(), name='send_test_links_bulk'),
    path('<uuid:test_token>/questions/', RetrieveTestQuestionsView.as_view(), name='retrieve_test_questions'),
    path('<uuid:test_token>/submit/', SubmitTestAnswersView.as_view(), name='submit_test_answers'),
    path('rank-students/<int:job_id>/', RankStudentsByJobView.as_view(), name='rank_students_by_job'),
]

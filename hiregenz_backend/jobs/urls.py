from django.urls import path
from .views import JobPostListCreateView, JobPostDetailView

urlpatterns = [
    # List all job posts or create a new job post
    path('job-posts/', JobPostListCreateView.as_view(), name='job_post_list_create'),

    # Retrieve, update, or delete a specific job post
    path('job-posts/<int:pk>/', JobPostDetailView.as_view(), name='job_post_detail'),
]
from django.urls import path
from .views import JobPostView

urlpatterns = [
    path('', JobPostView.as_view()),
]

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),  # Include users app URLs
    path('api/jobs/', include('jobs.urls')),  # Include jobs app URLs
    path('api/applications/', include('applications.urls')),  # Include applications app URLs
    path('api/tests/', include('tests.urls')),  # Include tests app URLs
    path('api/matching/', include('matching.urls')),  # Include matching app URLs
]

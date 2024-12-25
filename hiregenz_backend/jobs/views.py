from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from .models import JobPost
from .serializers import JobPostSerializer
from helpers.permission import IsRecruiter
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404


class JobPostListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsRecruiter]

    def get(self, request, *args, **kwargs):
        job_posts = JobPost.objects.all()
        serializer = JobPostSerializer(job_posts, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = JobPostSerializer(data=request.data, context={'request': request})  # Pass context
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=400)


class JobPostDetailView(APIView):
    """
    API View to retrieve, update, or delete a specific job post.
    """
    permission_classes = [IsAuthenticated]  # Default for PUT and DELETE

    def get_permissions(self):
        # Allow unauthenticated access for GET; enforce authentication for others
        if self.request.method == 'GET':
            return [AllowAny()]
        return super().get_permissions()

    def get(self, request, pk, *args, **kwargs):
        # Retrieve a job post
        job_post = get_object_or_404(JobPost, pk=pk)
        serializer = JobPostSerializer(job_post)
        return Response(serializer.data, status=HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        # Update a job post (only recruiters can update their own job posts)
        job_post = get_object_or_404(JobPost, pk=pk, recruiter=request.user.recruiter_profile)
        serializer = JobPostSerializer(job_post, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk, *args, **kwargs):
        # Delete a job post (only recruiters can delete their own job posts)
        job_post = get_object_or_404(JobPost, pk=pk, recruiter=request.user.recruiter_profile)
        job_post.delete()
        return Response({"message": "Job post deleted successfully"}, status=HTTP_204_NO_CONTENT)
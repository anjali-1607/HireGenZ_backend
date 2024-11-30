from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED
from .models import JobPost
from .serializers import JobPostSerializer
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_204_NO_CONTENT
from django.shortcuts import get_object_or_404

class JobPostListCreateView(APIView):
    """
    API View to list all job posts or create a new job post.
    """

    def get(self, request, *args, **kwargs):
        job_posts = JobPost.objects.all()
        serializer = JobPostSerializer(job_posts, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = JobPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=400)


class JobPostDetailView(APIView):
    """
    API View to retrieve, update, or delete a specific job post.
    """

    def get(self, request, pk, *args, **kwargs):
        job_post = get_object_or_404(JobPost, pk=pk)
        serializer = JobPostSerializer(job_post)
        return Response(serializer.data, status=HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        job_post = get_object_or_404(JobPost, pk=pk)
        serializer = JobPostSerializer(job_post, data=request.data, partial=True)  # Allow partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk, *args, **kwargs):
        job_post = get_object_or_404(JobPost, pk=pk)
        job_post.delete()
        return Response({"message": "Job post deleted successfully"}, status=HTTP_204_NO_CONTENT)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import JobPost
from .serializers import JobPostSerializer

class JobPostView(APIView):
    def post(self, request):
        serializer = JobPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        job_posts = JobPost.objects.filter(is_active=True)
        serializer = JobPostSerializer(job_posts, many=True)
        return Response(serializer.data)

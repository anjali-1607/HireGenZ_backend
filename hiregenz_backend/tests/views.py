from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import TestQuestion, TestResult
from .serializers import TestQuestionSerializer, TestResultSerializer

class TestQuestionView(APIView):
    def post(self, request):
        serializer = TestQuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TestResultView(APIView):
    def post(self, request):
        serializer = TestResultSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        results = TestResult.objects.all()
        serializer = TestResultSerializer(results, many=True)
        return Response(serializer.data)

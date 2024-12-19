from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from .utils.parser import parse_resume
from .utils.analyzer import analyze_resume, score_resume
from .utils.genai import generate_feedback


class ResumeAnalysisView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        resume_file = request.FILES.get('resume')
        if not resume_file:
            return Response({"error": "No file uploaded."}, status=400)

        try:
            # Parse resume
            content = parse_resume(resume_file)

            # Analyze and score
            analysis = analyze_resume(content)
            scores = score_resume(content)

            # Generate feedback using GenAI
            feedback = generate_feedback(content)

            return Response({
                "analysis": analysis,
                "scores": scores,
                "feedback": feedback,
            })
        except Exception as e:
            return Response({"error": str(e)}, status=500)

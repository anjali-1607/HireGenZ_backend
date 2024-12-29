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
            contact_info = analysis.get("contact_info", {})
            emails = contact_info.get("emails", [])
            if not emails:
                # If no email is found, do not generate feedback
                return Response({
                    "message": "Resume Quality is Poor. Email information is required for analysis.",
                    "analysis": analysis,
                    "scores": None,
                    "feedback": None,
                }, status=400)

            # Generate feedback only if email exists
            scores = score_resume(content)
            feedback = generate_feedback(content)

            return Response({
                "message": "Resume analyzed successfully.",
                "analysis": analysis,
                "scores": scores,
                "feedback": feedback,
            })
        except Exception as e:
            return Response({"error": str(e)}, status=500)
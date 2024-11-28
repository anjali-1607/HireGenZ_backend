from rest_framework.views import APIView
from rest_framework.response import Response
from users.models import Candidate
from jobs.models import JobPost

class MatchingView(APIView):
    def get(self, request, job_id):
        job_post = JobPost.objects.get(id=job_id)
        candidates = Candidate.objects.all()

        # Basic matching logic (can be extended with AI/ML)
        matched_candidates = [
            candidate for candidate in candidates
            if set(candidate.preferences.get('skills', [])).intersection(set(job_post.key_skills))
        ]

        # Returning matched candidate names for simplicity
        matched_data = [{"name": candidate.name, "email": candidate.email} for candidate in matched_candidates]
        return Response(matched_data)

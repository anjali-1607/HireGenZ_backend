from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from django.shortcuts import get_object_or_404
from users.models import Candidate
from jobs.models import JobPost
from .matching import match_candidate_to_job


class MatchCandidatesView(APIView):
    """
    API View to match candidates to a specific job and return ranked results.
    """

    def get(self, request, job_id, *args, **kwargs):
        # Fetch the job
        job = get_object_or_404(JobPost, id=job_id)

        # Fetch all candidates
        candidates = Candidate.objects.all()

        # Rank candidates by match score
        ranked_candidates = [
            {
                "candidate_id": candidate.id,
                "name": candidate.name,
                "score": match_candidate_to_job(candidate, job),
            }
            for candidate in candidates
        ]

        # Sort candidates by score in descending order
        ranked_candidates = sorted(ranked_candidates, key=lambda x: x["score"], reverse=True)

        # Return response
        return Response(
            {
                "job_id": job.id,
                "job_title": job.title,
                "matches": ranked_candidates,
            },
            status=HTTP_200_OK,
        )


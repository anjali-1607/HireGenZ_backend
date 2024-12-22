from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from django.shortcuts import get_object_or_404
from django.conf import settings
from users.models import Candidate
from jobs.models import JobPost
from .matching import match_candidate_to_job
from helpers.permission import IsRecruiter  # Import the IsRecruiter permission


class MatchCandidatesPagination(PageNumberPagination):
    """
    Custom pagination class for matching candidates.
    """
    page_size = 20  # Number of candidates per page
    page_size_query_param = 'page_size'  # Allow the client to control page size
    max_page_size = 100  # Maximum allowed page size


class MatchCandidatesView(APIView):
    """
    API View to match candidates to a specific job and return ranked results with pagination.
    """

    def get(self, request, job_id, *args, **kwargs):
        # Check if the user is a recruiter
        if not IsRecruiter().has_permission(request, self):
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=HTTP_403_FORBIDDEN
            )

        try:
            # Fetch the job
            job = get_object_or_404(JobPost, id=job_id)

            # Fetch only required fields from candidates using optimized query
            candidates = Candidate.objects.only(
                "id", "name", "email", "resume_file", "skills"
            ).all()

            if not candidates.exists():
                return Response(
                    {"detail": "No candidates found."},
                    status=HTTP_404_NOT_FOUND
                )

            # Optimize matching by using lazy evaluation and batching
            ranked_candidates = []
            for candidate in candidates.iterator():  # Use iterator for batch processing
                score = match_candidate_to_job(candidate, job)
                ranked_candidates.append({
                    "candidate_id": candidate.id,
                    "name": candidate.name,
                    "email": candidate.email,
                    "resume_file": self.get_resume_url(candidate.resume_file),
                    "score": score,
                })

            # Sort candidates by score in descending order
            ranked_candidates.sort(key=lambda x: x["score"], reverse=True)

            # Calculate total candidates matched
            total_matched = len(ranked_candidates)

            # Apply pagination
            paginator = MatchCandidatesPagination()
            paginated_data = paginator.paginate_queryset(ranked_candidates, request)

            # Return paginated response
            return paginator.get_paginated_response({
                "job_id": job.id,
                "job_title": job.title,
                "total_matched": total_matched,  # Include the total count of matched candidates
                "matches": paginated_data,
            })

        except JobPost.DoesNotExist:
            return Response(
                {"detail": "Job post not found."},
                status=HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": f"An unexpected error occurred: {str(e)}"},
                status=HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_resume_url(self, resume_file):
        """
        Generate the full URL for the candidate's resume file.
        """
        if resume_file and resume_file.url:
            return f"{settings.MEDIA_URL}{resume_file.name}"
        return None

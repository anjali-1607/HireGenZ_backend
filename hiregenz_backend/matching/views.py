from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from django.shortcuts import get_object_or_404
from users.models import Candidate, CandidatePreference
from jobs.models import JobPost
from .matching import match_candidate_to_job


class GetMatchedCandidatesView(APIView):
    def get(self, request, job_id):
        try:
            job_post = JobPost.objects.get(id=job_id)
            candidates = Candidate.objects.all()

            matched_candidates = []

            for candidate in candidates:
                # Example matching logic
                candidate_skills = set(candidate.preferences.get('skills', []))
                job_skills = set(job_post.key_skills)

                # Calculate match score based on skills
                skill_match_score = len(candidate_skills.intersection(job_skills)) / len(job_skills) * 100 if job_skills else 0

                # Optional: Add additional scoring logic (e.g., experience, location, etc.)
                match_score = skill_match_score

                if match_score > 0:  # Include only candidates with non-zero match scores
                    matched_candidates.append({
                        'candidate': candidate,
                        'job_post': job_post,
                        'match_score': match_score
                    })

            # Rank candidates by match_score in descending order
            matched_candidates.sort(key=lambda x: x['match_score'], reverse=True)

            # Save matches in the database
            matches = []
            for match in matched_candidates:
                match_instance, created = Match.objects.update_or_create(
                    candidate=match['candidate'],
                    job_post=match['job_post'],
                    defaults={'match_score': match['match_score']}
                )
                matches.append(match_instance)

            # Serialize and return the ranked results
            serializer = MatchSerializer(matches, many=True)
            return Response(serializer.data)

        except JobPost.DoesNotExist:
            return Response({'error': 'Job post not found'}, status=404)
        




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


from rest_framework.views import APIView
from rest_framework.response import Response
from users.models import Candidate
from jobs.models import JobPost
from .models import Match
from .serializers import MatchSerializer

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

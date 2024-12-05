from django.core.mail import send_mail
from django.utils.timezone import now
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db.models import F, ExpressionWrapper, DurationField
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Test
from jobs.models import JobPost
from users.models import Candidate

from .utils import generate_mcqs


class SendTestLinksToShortlistedView(APIView):
    """
    API to send test links to all shortlisted candidates.
    """

    def post(self, request, job_id, *args, **kwargs):
        # Ensure the job exists
        job = get_object_or_404(JobPost, id=job_id)

        # Retrieve shortlisted candidates from the request
        shortlisted_candidates = request.data.get('shortlisted_candidates', [])

        if not shortlisted_candidates:
            return Response({"error": "No shortlisted candidates provided."}, status=400)

        # Check if MCQs are already generated for the job
        if not job.mcqs:  # Assuming you already added an `mcqs` field to JobPost for this purpose
            job.mcqs = generate_mcqs(job.description)
            job.save()

        for candidate_id in shortlisted_candidates:
            candidate = get_object_or_404(Candidate, id=candidate_id)

            # Save test to the database using the stored MCQs in the `questions` column
            test = Test.objects.create(
                candidate=candidate,
                recruiter=job.recruiter,
                job_description=job.description,
                questions=job.mcqs,  # Store MCQs in the `questions` column
            )

            # Generate test link using the test token
            test_link = f"https://yourdomain.com/tests/{test.test_token}/"

            # Send email to the candidate
            send_mail(
                subject="Your Resume is Shortlisted - Attempt the Test",
                message=f"""
                Dear {candidate.name},

                Congratulations! Your resume has been shortlisted for the {job.title} position at {job.recruiter.company_name}.
                To proceed, please attempt the test using the following link:
                {test_link}

                Note: Failing to complete the test may disqualify you from this opportunity.

                Best regards,
                {job.recruiter.company_name}
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[candidate.email],
            )

        return Response({"message": "Tests generated and emails sent successfully."}, status=200)
    

class RetrieveTestQuestionsView(APIView):
    def get(self, request, test_token, *args, **kwargs):
        # Fetch the test using the token
        test = get_object_or_404(Test, test_token=test_token, is_completed=False)

        # Update the started_at timestamp if it is not already set
        if not test.started_at:
            test.started_at = now()
            test.save()

        # Remove the 'answer' field from each question for candidate view
        questions = [
            {
                "question": q["question"],
                "options": q["options"]
            }
            for q in test.questions
        ]

        return Response({
            "candidate_name": test.candidate.name,
            "questions": questions
        }, status=200)
    


class SubmitTestAnswersView(APIView):
    def post(self, request, test_token, *args, **kwargs):
        # Fetch the test using the token
        test = get_object_or_404(Test, test_token=test_token, is_completed=False)

        # Get submitted answers
        submitted_answers = request.data.get('answers')
        if not submitted_answers:
            return Response({"error": "Answers are required."}, status=400)

        # Validate submitted answers against correct answers
        correct_answers = {q['question']: q['answer'] for q in test.questions}
        score = 0

        for question, answer in submitted_answers.items():
            if correct_answers.get(question) == answer:
                score += 1

        # Save the test results
        test.candidate_answers = submitted_answers
        test.score = score
        test.is_completed = True
        test.save()  # `submitted_at` is updated automatically in the model

        # Send confirmation email
        send_mail(
            subject="Thank You for Submitting the Test",
            message=f"""
            Dear {test.candidate.name},

            Thank you for completing the test for the {test.recruiter.company_name} position. If selected, we will get back to you soon.

            Thanks and Regards,
            HireGenzo Team
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test.candidate.email],
        )

        return Response({
            "message": "Test submitted successfully.",
            "score": score,
            "total_questions": len(correct_answers)
        }, status=200)
    


class RankStudentsByJobView(APIView):
    """
    API to rank candidates based on their test scores and time taken for a specific job.
    """

    def get(self, request, job_id, *args, **kwargs):
        # Validate that the Job Post exists
        job = get_object_or_404(JobPost, id=job_id)

        # Fetch completed tests for the given Job Post
        completed_tests = Test.objects.filter(
            recruiter=job.recruiter,  # Ensure tests are tied to the recruiter
            is_completed=True
        ).annotate(
            time_taken=ExpressionWrapper(
                F('submitted_at') - F('started_at'),
                output_field=DurationField()
            )
        )

        # Sort tests by score (descending) and time_taken (ascending)
        sorted_tests = sorted(
            completed_tests,
            key=lambda x: (-x.score, x.time_taken.total_seconds() if x.time_taken else float('inf'))
        )

        # Prepare the ranking
        ranking = []
        rank = 1
        for test in sorted_tests:
            time_taken = test.time_taken.total_seconds() if test.time_taken else None
            ranking.append({
                "rank": rank,
                "candidate_name": test.candidate.name,
                "score": test.score,
                "time_taken": time_taken  # Time in seconds
            })
            rank += 1

        return Response({
            "job_title": job.title,
            "ranking": ranking
        }, status=200)
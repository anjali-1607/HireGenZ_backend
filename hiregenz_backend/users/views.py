import os
import random
import string
from tempfile import NamedTemporaryFile
from pdfminer.high_level import extract_text
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from .models import Recruiter, Candidate, CandidatePreference
from .serializers import RecruiterSerializer, CandidateSerializer
from .utils import extract_resume_data  # Utility for parsing resumes

class ResumeUploadView(APIView):
    """Handles the uploading and parsing of resumes, sending OTP for email verification."""

    def post(self, request):
        try:
            # Validate resume file
            resume_file = self.get_uploaded_file(request)
            resume_text = self.extract_resume_text(resume_file)

            # Parse resume data
            extracted_data = extract_resume_data(resume_text)
            email = extracted_data.get("email")

            if not email:
                return Response({"error": "No valid email found in the resume."}, status=status.HTTP_400_BAD_REQUEST)

            # Create or update candidate
            candidate, message, is_new_or_unverified = self.create_or_update_candidate(
                extracted_data, resume_file, resume_text
            )

            # Send OTP only if the candidate is new or unverified
            if is_new_or_unverified:
                otp = self.generate_otp()
                candidate.otp = otp
                candidate.is_verified = False
                candidate.save()
                self.send_otp_email(candidate.email, otp)

                return Response(
                    {"message": f"{message} OTP sent to {candidate.email} for verification."},
                    status=status.HTTP_201_CREATED,
                )

            return Response(
                {"message": f"{message} Candidate already verified."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_uploaded_file(self, request):
        """Fetch the uploaded resume file."""
        if not request.FILES.get("resume"):
            raise ValueError("No resume file provided.")
        return request.FILES["resume"]

    def extract_resume_text(self, resume_file):
        """Extract text from the uploaded resume file."""
        temp_file = NamedTemporaryFile(delete=False)
        temp_file.write(resume_file.read())
        temp_file.flush()
        resume_text = extract_text(temp_file.name)
        temp_file.close()
        os.unlink(temp_file.name)
        return resume_text

    def create_or_update_candidate(self, extracted_data, resume_file, resume_text):
        """Create or update a candidate record based on extracted resume data."""
        email = extracted_data.get("email")
        candidate = Candidate.objects.filter(email=email).first()

        if candidate:
            if not candidate.is_verified:  # Candidate exists but is not verified
                for field, value in extracted_data.items():
                    setattr(candidate, field, value)
                candidate.resume_file = resume_file
                candidate.resume_text = resume_text
                candidate.save()
                return candidate, "Candidate details updated successfully!", True
            else:  # Candidate exists and is already verified
                return candidate, "Candidate details updated successfully!", False
        else:
            # Create a new candidate
            candidate = Candidate.objects.create(
                name=extracted_data.get("name"),
                email=email,
                phone=extracted_data.get("phone"),
                skills=", ".join(extracted_data.get("skills", [])),
                certifications=extracted_data.get("certifications"),
                education=extracted_data.get("education"),
                work_experience=extracted_data.get("work_experience"),
                professional_summary=extracted_data.get("professional_summary"),
                resume_text=resume_text,
                resume_file=resume_file,
            )
            return candidate, "Candidate created successfully!", True

    def generate_otp(self):
        """Generate a 6-digit OTP."""
        return ''.join(random.choices(string.digits, k=6))

    def send_otp_email(self, email, otp):
        """Send an OTP email to the candidate."""
        subject = "Verify Your Email - HireGenZ"
        message = f"Your OTP for email verification is: {otp}. Please verify to complete your registration."
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        except Exception as e:
            print(f"Error sending OTP email: {e}")

class VerifyEmailView(APIView):
    """Handles email verification via OTP and updates candidate preferences."""

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        preferences_data = request.data.get("preferences", {})

        if not email or not otp:
            return Response({"error": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        candidate = Candidate.objects.filter(email=email).first()
        if not candidate:
            return Response({"error": "Candidate not found."}, status=status.HTTP_404_NOT_FOUND)

        if candidate.otp == otp:
            candidate.is_verified = True
            candidate.otp = None  # Clear OTP after verification
            candidate.save()

            # Handle candidate preferences if provided
            self.update_preferences(candidate, preferences_data)

            # Send a welcome email after successful verification
            self.send_welcome_email(candidate.email, candidate.name)

            return Response({"message": "Email verified successfully and preferences updated."}, status=status.HTTP_200_OK)

        return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

    def send_welcome_email(self, email, name):
        """Send a welcome email after successful verification."""
        subject = "Welcome to HireGenZ!"
        message = (
            f"Hi {name},\n\n"
            "Congratulations! Your email has been successfully verified. "
            "You can now explore the features of HireGenZ.\n\n"
            "Thank you for joining us!"
        )
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        except Exception as e:
            print(f"Error sending welcome email: {e}")

    def update_preferences(self, candidate, preferences_data):
        """Update or create preferences for the candidate."""
        if not preferences_data:
            return

        # Extract preferences data
        expected_salary_min = preferences_data.get("expected_salary_min")
        expected_salary_max = preferences_data.get("expected_salary_max")
        preferred_locations = preferences_data.get("preferred_locations", [])
        job_type = preferences_data.get("job_type")
        employment_type = preferences_data.get("employment_type")

        # Update or create candidate preferences
        CandidatePreference.objects.update_or_create(
            candidate=candidate,
            defaults={
                "expected_salary_min": expected_salary_min,
                "expected_salary_max": expected_salary_max,
                "preferred_locations": preferred_locations,
                "job_type": job_type,
                "employment_type": employment_type,
            },
        )
class RecruiterView(APIView):
    """Handles recruiter creation."""

    def post(self, request):
        serializer = RecruiterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class CandidateView(APIView):
#     """Handles candidate creation with or without resume upload."""

#     def post(self, request):
#         print("Runned!")
#         try:
#             # Check for resume upload
#             if request.FILES.get("resume"):
#                 resume_file = self.get_uploaded_file(request)
#                 resume_text = self.extract_resume_text(resume_file)

#                 # Extract structured data from the resume
#                 extracted_data = extract_resume_data(resume_text)

#                 # Create or update candidate
#                 candidate, message = self.create_or_update_candidate(extracted_data, resume_file, resume_text)

#                 print("Candidate, Message",candidate, message)

#                 # Send email notification
#                 if candidate.email:
#                     self.send_email(candidate.email, candidate.name, is_new=not candidate.is_verified)
#                 else:
#                     print("No valid email address provided for the candidate.")
                

#                 return Response(
#                     {"message": message, "data": CandidateSerializer(candidate).data},
#                     status=status.HTTP_201_CREATED,
#                 )

#             # Handle direct data creation
#             else:
#                 print("Running")
#                 serializer = CandidateSerializer(data=request.data)
#                 if serializer.is_valid():
#                     serializer.save()
#                     return Response(serializer.data, status=status.HTTP_201_CREATED)
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def get_uploaded_file(self, request):
#         """Fetch the uploaded resume file."""
#         if not request.FILES.get("resume"):
#             raise ValueError("No resume file provided.")
#         return request.FILES["resume"]

#     def extract_resume_text(self, resume_file):
#         """Extract text from the uploaded resume file."""
#         temp_file = NamedTemporaryFile(delete=False)
#         temp_file.write(resume_file.read())
#         temp_file.flush()
#         resume_text = extract_text(temp_file.name)
#         temp_file.close()
#         os.unlink(temp_file.name)
#         return resume_text

#     def create_or_update_candidate(self, extracted_data, resume_file, resume_text):
#         """Create or update a candidate record."""
#         email = extracted_data.get("email")
#         candidate = Candidate.objects.filter(email=email).first()

#         if candidate:
#             for field, value in extracted_data.items():
#                 setattr(candidate, field, value)
#             candidate.resume_file = resume_file
#             candidate.save()
#             return candidate, "Candidate details updated successfully!"
#         else:
#             candidate = Candidate.objects.create(
#                 name=extracted_data["name"],
#                 email=email,
#                 phone=extracted_data["phone"],
#                 skills=", ".join(extracted_data["skills"]),
#                 certifications=extracted_data["certifications"],
#                 education=extracted_data["education"],
#                 work_experience=extracted_data["work_experience"],
#                 professional_summary=extracted_data["professional_summary"],
#                 resume_text=resume_text,
#                 resume_file=resume_file,
#             )
#             return candidate, "Candidate created successfully!"

#     def send_email(self, email, name, is_new=True):
#         """Send welcome or update notification email."""
#         subject = "Welcome to HireGenZ!" if is_new else "Your Profile Was Updated"
#         message = (
#             f"Hi {name},\n\n"
#             "Thank you for uploading your resume. We have successfully created your profile!"
#             if is_new
#             else f"Hi {name},\n\nYour profile has been successfully updated with your new resume."
#         )
#         try:
#             send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
#         except BadHeaderError:
#             raise ValueError("Invalid header found.")
#         except Exception as e:
#             print(f"Error sending email: {e}")
#             raise

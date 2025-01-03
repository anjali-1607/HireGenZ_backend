import random
import string
import boto3
from io import BytesIO
from pdfminer.high_level import extract_text
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from django.core.mail import send_mail
from rest_framework import status
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import Recruiter, Candidate, CandidatePreference
from .serializers import RecruiterSerializer, OTPVerificationSerializer, RecruiterOTPLoginSerializer
from .utils import extract_resume_data, TokenUtility  # Utility for parsing resumes


class ResumeUploadView(APIView):
    """Handles the uploading and parsing of resumes, sending OTP for email verification or preference updates."""

    def post(self, request):
        try:
            # Validate and retrieve the resume file
            resume_file = self.get_uploaded_file(request)
            resume_text = self.extract_resume_text(resume_file)
            # print(resume_text)
            # Parse resume data
            extracted_data = extract_resume_data(resume_text)
            print("Extractted Data", extracted_data)
            email = extracted_data.get("email")
            if not email:
                return Response({"error": "No valid email found in the resume."}, status=status.HTTP_400_BAD_REQUEST)

            # Create or update candidate
            candidate, message, is_new_or_requires_verification = self.create_or_update_candidate(
                extracted_data, resume_file, resume_text
            )

            # Check if OTP is required
            if is_new_or_requires_verification:
                if not candidate.is_verified:
                    # Send OTP for email verification
                    otp = self.generate_otp()
                    candidate.otp = otp
                    candidate.is_verified = False
                    candidate.save()
                    self.send_otp_email(candidate.email, otp, candidate.name)

                    return Response(
                        {
                            "message": f"{message} OTP sent to {candidate.email} for verification.",
                            "data": {"email": candidate.email, "is_verified": "false"},
                        },
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    # Send OTP for preference updates
                    otp = self.generate_otp()
                    candidate.otp = otp
                    candidate.save()
                    self.send_otp_email(candidate.email, otp, candidate.name)

                    return Response(
                        {
                            "message": "OTP sent for updating preferences.",
                            "data": {"email": candidate.email, "is_verified": "true"},
                        },
                        status=status.HTTP_200_OK,
                    )

            # No OTP required (email already verified, no preference update needed)
            return Response(
                {
                    "message": f"{message} Candidate already verified and no further action is needed.",
                    "data": {"email": candidate.email, "is_verified": "true"},
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_uploaded_file(self, request):
        """Fetch the uploaded resume file."""
        resume_file = request.FILES.get("resume")
        if not resume_file:
            raise ValueError("No resume file provided.")
        return resume_file
    
    def extract_resume_text(self, file):
        """
        Extract text content from a PDF resume file.
        """
        try:
            # Convert the InMemoryUploadedFile to a file-like object (BytesIO)
            file_content = BytesIO(file.read())
            
            # Extract text from the PDF content
            content = extract_text(file_content)
            
            return content
        except Exception as e:
            raise ValueError(f"Error extracting text from resume: {str(e)}")

    def upload_to_s3(self, file_obj, filename):
        """Upload the resume file to AWS S3 and return the public URL."""
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        s3_path = f"resumes/{filename}"

        # Upload the file to the specified S3 path
        s3.upload_fileobj(file_obj, bucket_name, s3_path)

        # Construct the URL for the uploaded file
        url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{s3_path}"
        return url

    def create_or_update_candidate(self, extracted_data, resume_file, resume_text):
        """Create or update a candidate record based on extracted resume data."""
        from django.contrib.auth import get_user_model
        User = get_user_model()

        email = extracted_data.get("email")
        candidate = Candidate.objects.filter(email=email).first()

        # Generate a unique filename for the resume
        filename = f"{email.replace('@', '_').replace('.', '_')}_resume.pdf"

        # Upload resume to S3
        resume_url = self.upload_to_s3(resume_file, filename)

        if candidate:
            if not candidate.is_verified:  # Candidate exists but is not verified
                for field, value in extracted_data.items():
                    setattr(candidate, field, value)
                candidate.resume_file = resume_url
                candidate.resume_text = resume_text
                candidate.save()
                return candidate, "Candidate details updated successfully!", True
            else:  # Candidate exists, already verified (send OTP for preferences update)
                return candidate, "Candidate details updated successfully!", True
        else:
            # Create a new user
            user = User.objects.create_user(
                username=email,  # Use email as the username
                email=email,
                password=''.join(random.choices(string.ascii_letters + string.digits, k=8)),  # Example: 8-character password
                role='candidate'  # Set the role for the user
            )

            # Create a new candidate linked to the user
            candidate = Candidate.objects.create(
                user=user,
                name=extracted_data.get("name"),
                email=email,
                phone=extracted_data.get("phone"),
                skills=", ".join(extracted_data.get("skills", [])),
                certifications=extracted_data.get("certifications"),
                education=extracted_data.get("education"),
                work_experience=extracted_data.get("work_experience"),
                total_work_experience=extracted_data.get("total_experience"),
                professional_summary=extracted_data.get("professional_summary"),
                resume_text=resume_text,
                resume_file=resume_url,
            )
            return candidate, "Candidate created successfully!", True

    def generate_otp(self):
        """Generate a 6-digit OTP."""
        return ''.join(random.choices(string.digits, k=6))

    def send_otp_email(self, email, otp, name):
        """Send an OTP email to the candidate with an HTML template."""
        subject = "Verify Your Email - HireGenZ"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [email]

        # Render the HTML template with context
        html_content = render_to_string('verification_email.html', {'name': name, 'otp': otp})

        # Create the email
        email_message = EmailMultiAlternatives(subject, "", from_email, to_email)
        email_message.attach_alternative(html_content, "text/html")

        try:
            email_message.send()
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

        # Fetch candidate by email
        candidate = Candidate.objects.filter(email=email).first()
        if not candidate:
            return Response({"error": "Candidate not found."}, status=status.HTTP_404_NOT_FOUND)

        # Validate OTP
        if candidate.otp != otp:
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        # OTP matches
        if not candidate.is_verified:
            # First-time email verification
            candidate.is_verified = True
            candidate.otp = None  # Clear OTP after verification
            candidate.save()

            # Handle candidate preferences if provided
            self.update_preferences(candidate, preferences_data)

            # Send a welcome email after successful first-time verification
            self.send_welcome_email(candidate.email, candidate.name)

            return Response(
                {"message": "Email verified successfully and preferences updated."},
                status=status.HTTP_200_OK,
            )
        else:
            # Candidate already verified; proceed with updating preferences
            candidate.otp = None  # Clear OTP after successful update
            candidate.save()

            # Handle candidate preferences
            self.update_preferences(candidate, preferences_data)

            return Response(
                {"message": "Preferences updated successfully."},
                status=status.HTTP_200_OK,
            )

    def send_welcome_email(self, email, name):
        """Send a welcome email after successful first-time verification."""
        subject = "Welcome to HireGenZo!"
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


class RecruiterRegistrationView(APIView):
    """
    API for registering recruiters and sending OTPs.
    """
    def post(self, request, *args, **kwargs):
        serializer = RecruiterSerializer(data=request.data)
        if serializer.is_valid():
            recruiter = serializer.save()
            recruiter.generate_otp()  # Generate OTP
            # Send OTP to the recruiter's email
            send_mail(
                subject="Verify Your Email",
                message=f"Your OTP is {recruiter.otp}. It is valid for 10 minutes.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recruiter.email],
            )
            return Response({"message": "Recruiter registered successfully. OTP sent to email."}, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class OTPVerificationView(APIView):
    """
    API for verifying OTP and activating the recruiter account.
    """
    def post(self, request, *args, **kwargs):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            recruiter = serializer.validated_data
            recruiter.is_verified = True
            recruiter.otp = None  # Clear OTP after successful verification
            recruiter.otp_expiration = None
            recruiter.save()

            # Generate JWT tokens using TokenUtility
            tokens = TokenUtility.get_tokens_for_user(recruiter.user)
           
            return Response({
                "message": "Email verified successfully.",
                "tokens": tokens,
                "recruiter_id": recruiter.id
            }, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class SendOTPForLoginView(APIView):
    """
    API to send OTP for recruiter login.
    """

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required."}, status=HTTP_400_BAD_REQUEST)

        try:
            recruiter = Recruiter.objects.get(email=email)
        except Recruiter.DoesNotExist:
            return Response({"error": "Recruiter not found."}, status=HTTP_400_BAD_REQUEST)

        # **Generate and send OTP, regardless of email verification status**
        recruiter.generate_otp()
        send_mail(
            subject="Your OTP for Login",
            message=f"Your OTP for login is {recruiter.otp}. It is valid for 10 minutes.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return Response({"message": "OTP sent to your email."}, status=HTTP_200_OK)


class RecruiterOTPLoginView(APIView):
    """
    API to log in recruiters using email and OTP with JWT tokens.
    """

    def send_welcome_email(self, recruiter):
        """Send a welcome email to the recruiter."""
        subject = "Welcome to HireGenZo!"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [recruiter.email]

        # Render the HTML template with context
        html_content = render_to_string('welcome_recuiters.html', {'name': recruiter.name})

        # Create the email
        email_message = EmailMultiAlternatives(subject, "", from_email, to_email)
        email_message.attach_alternative(html_content, "text/html")

        try:
            # Send the email
            email_message.send()
        except Exception as e:
            print(f"Error sending welcome email: {e}")

    def post(self, request, *args, **kwargs):
        serializer = RecruiterOTPLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            recruiter = serializer.validated_data

            # Check if the recruiter is being verified for the first time
            if not recruiter.is_verified:
                self.send_welcome_email(recruiter)
                recruiter.is_verified = True  # Mark the welcome email as sent
                recruiter.save()

            # Generate JWT tokens using TokenUtility
            tokens = TokenUtility.get_tokens_for_user(recruiter.user)

            # Clear OTP after successful login
            recruiter.otp = None
            recruiter.otp_expiration = None
            recruiter.save()

            return Response(
                {
                    "message": "Login successful.",
                    "tokens": tokens,
                    "recruiter_id": recruiter.id,
                },
                status=HTTP_200_OK,
            )
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

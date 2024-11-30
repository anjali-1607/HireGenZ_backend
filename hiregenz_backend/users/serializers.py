from rest_framework import serializers
from .models import Recruiter, Candidate
from django.utils.timezone import now
import requests
import re
from urllib.parse import urlparse

class RecruiterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recruiter
        fields = ["name",'email', 'company_name', 'website_url', 'is_verified']

    def validate_email(self, email):
        

        # Restrict registration to work emails (no personal emails)
        if re.match(r'.+@(gmail\.com|yahoo\.com|hotmail\.com|outlook\.com)$', email):
            raise serializers.ValidationError("Only work email addresses are allowed.")
        
        # Extract the domain from the website URL
        website_url = self.initial_data.get('website_url')
        if not website_url:
            raise serializers.ValidationError("Website URL is required to validate the email.")

        # Parse the website domain
        parsed_url = urlparse(website_url)
        website_domain = parsed_url.netloc.replace("www.", "").lower()

        # Extract the domain from the email
        email_domain = email.split('@')[-1].lower()

        # Validate that the email domain matches the website domain
        if website_domain not in email_domain:
            raise serializers.ValidationError(
                "The email domain must match the company website domain."
            )
        
        return email



    def validate_website_url(self, website_url):
        # Check if the provided website is reachable
        try:
            response = requests.head(website_url, timeout=5)
            if response.status_code >= 400:
                raise serializers.ValidationError("The company website is not reachable.")
        except requests.RequestException:
            raise serializers.ValidationError("The company website is not reachable.")
        return website_url


class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data.get('email')
        otp = data.get('otp')

        try:
            recruiter = Recruiter.objects.get(email=email)
        except Recruiter.DoesNotExist:
            raise serializers.ValidationError("Recruiter not found.")

        # Check OTP validity
        if recruiter.otp != otp or recruiter.otp_expiration < now():
            raise serializers.ValidationError("Invalid or expired OTP.")
        return recruiter

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = '__all__'

from rest_framework import serializers
from .models import JobPost


class JobPostSerializer(serializers.ModelSerializer):
    recruiter_id = serializers.IntegerField(source='recruiter.id', read_only=True)  # Add recruiter_id as read-only

    class Meta:
        model = JobPost
        exclude = ['recruiter']  # Exclude recruiter from input

    def create(self, validated_data):
        # Get the recruiter from the request context
        request = self.context.get('request')
        if not request or not hasattr(request.user, 'recruiter_profile'):
            raise serializers.ValidationError("Recruiter information is missing or invalid.")
        
        validated_data['recruiter'] = request.user.recruiter_profile  # Assign the recruiter from the token
        return super().create(validated_data)

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import Recruiter


class RecruiterJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication for the Recruiter model.
    """

    def get_user(self, validated_token):
        """
        Override to fetch the recruiter based on the token payload.
        """
        try:
            recruiter_id = validated_token['user_id']  # Assumes 'user_id' in JWT payload
            recruiter = Recruiter.objects.get(id=recruiter_id)
            return recruiter
        except Recruiter.DoesNotExist:
            raise AuthenticationFailed('No recruiter found for this token.')
        except KeyError:
            raise AuthenticationFailed('Invalid token payload.')

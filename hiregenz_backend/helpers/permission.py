from rest_framework.permissions import BasePermission


class IsRecruiter(BasePermission):
    """
    Allows access only to recruiters.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'recruiter'


class IsCandidate(BasePermission):
    """
    Allows access only to candidates.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'candidate'

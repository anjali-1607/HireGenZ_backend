from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Candidate, Recruiter


@receiver(post_delete, sender=Candidate)
def delete_user_on_candidate_delete(sender, instance, **kwargs):
    if instance.user:
        instance.user.delete()


@receiver(post_delete, sender=Recruiter)
def delete_user_on_recruiter_delete(sender, instance, **kwargs):
    if instance.user:
        instance.user.delete()

from django.db import models


class ContactInfo(models.Model):
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    social_links = models.JSONField(blank=True, null=True)  # Store social links as a list or dictionary
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

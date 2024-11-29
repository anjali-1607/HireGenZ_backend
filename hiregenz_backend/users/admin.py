from django.contrib import admin
from .models import Recruiter, Candidate, CandidatePreference

admin.site.register(Recruiter)
admin.site.register(Candidate)
admin.site.register(CandidatePreference)
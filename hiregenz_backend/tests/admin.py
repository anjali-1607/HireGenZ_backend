from django.contrib import admin
from .models import TestQuestion, TestResult

admin.site.register(TestQuestion)
admin.site.register(TestResult)

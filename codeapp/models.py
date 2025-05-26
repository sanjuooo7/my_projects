from django.db import models

# Create your models here.

class CodeSubmission(models.Model):
    student_name = models.CharField(max_length=100)
    code_file = models.FileField(upload_to='codes/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    output = models.TextField()
    errors = models.TextField()

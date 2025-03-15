from django.db import models

# Create your models here.
from django.db import models

class EmbeddedText(models.Model):
    page_num = models.IntegerField()
    text = models.TextField()
    embedding = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

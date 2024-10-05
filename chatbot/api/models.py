from django.db import models

# Create your models here.
# class Item(models.Model):
#     name = models.CharField(max_length=100)
#     description = models.TextField(max_length=300)
#     cost = models.IntegerField()

class User(models.Model):
    id=models.AutoField(primary_key=True, null=False)
    name=models.CharField(null=False, max_length=20)
    tel=models.CharField(null=False, max_length=20)
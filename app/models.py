from django.db import models
from django.contrib.auth.models import User
from datetime import date
# Create your models here.
# class User(models.Model):
#     userId = models.IntegerField(unique=True)
#     firstName = models.CharField(max_length=30)
#     lastName = models.CharField(max_length=30,null=True)
#     is_trainer = models.BooleanField(default=False)
#     def __str__(self) -> str:
#         return (str(self.userId))

class Conversation(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    id = models.IntegerField(unique=True,primary_key=True)
    human_query = models.TextField()
    bot_response = models.TextField()
    feedback = models.CharField(max_length=200,null=True, blank=True)
    description = models.CharField(max_length=1000,blank=True,null=True)
    metadata = models.JSONField(null=True, blank=True)

    def __str__(self) -> str:
        return str(self.id)

    

class FaissCollection(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    created = models.DateField()
    collection_name = models.CharField(max_length=100)
    file_path = models.FileField(upload_to='faiss_collections')
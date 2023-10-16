from django.db import models

# Create your models here.
class User(models.Model):
    userId = models.IntegerField(unique=True)
    firstName = models.CharField(max_length=30)
    lastName = models.CharField(max_length=30,null=True)
    is_trainer = models.BooleanField(default=False)
    def __str__(self) -> str:
        return (str(self.userId))

class Feedback(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    msgId = models.IntegerField()
    human_query = models.TextField()
    bot_response = models.TextField()
    feedback = models.CharField(max_length=200,null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)

    def __str__(self) -> str:
        return self.human_query

class ConversationMode(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    mode = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.mode
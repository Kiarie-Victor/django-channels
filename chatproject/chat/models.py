from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Message(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    time_stamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.author.username

    def last_10_messages():
        texts = Message.objects.order_by('-time_stamp').all()[:10]
        return texts
        
    
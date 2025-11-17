from django.db import models


class Profile(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    active = models.BooleanField(default=True)
    

    def __str__(self):
        return self.username

class StoryPersistance(models.Model):
    url = models.URLField(primary_key=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    downloaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.profile.username} - {self.url.split('/stories/')[1]}"

class ChatMessage(models.Model):
    chat_id = models.BigIntegerField()
    message_id = models.BigIntegerField()
    user_id = models.BigIntegerField()
    username = models.CharField(max_length=255, null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    photo_url = models.TextField(null=True, blank=True)
    caption = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['chat_id', 'message_id']
    
    def __str__(self):
        return f"{self.username}: {self.text[:50] if self.text else 'media'}"
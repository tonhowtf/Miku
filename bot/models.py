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
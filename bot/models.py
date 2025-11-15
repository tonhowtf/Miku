from django.db import models


class Profile(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    active = models.BooleanField(default=True)
    
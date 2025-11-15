from django.contrib import admin
from .models import Profile, StoryPersistance

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['username', 'active']
    list_filter = ['active']

@admin.register(StoryPersistance)
class StoryPersistanceAdmin(admin.ModelAdmin):
    list_display = ['url', 'profile', 'downloaded_at']
    list_filter = ['profile', 'downloaded_at']
    readonly_fields = ['downloaded_at']
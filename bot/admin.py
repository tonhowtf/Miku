from django.contrib import admin
from .models import Profile, StoryPersistance, ChatMessage

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['username', 'active']
    list_filter = ['active']

@admin.register(StoryPersistance)
class StoryPersistanceAdmin(admin.ModelAdmin):
    list_display = ['url', 'profile', 'downloaded_at']
    list_filter = ['profile', 'downloaded_at']
    readonly_fields = ['downloaded_at']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['username', 'text', 'chat_id', 'timestamp']
    list_filter = ['chat_id', 'timestamp']
    readonly_fields = ['timestamp']
    search_fields = ['username', 'text']
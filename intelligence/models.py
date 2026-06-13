from django.db import models
from django.contrib.auth.models import User

class ChatSession(models.Model):
    business = models.ForeignKey('core.Business', on_delete=models.CASCADE, related_name='chat_sessions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=200, default="New Conversation")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.created_at.date()})"

class ChatMessage(models.Model):
    SENDER_CHOICES = [
        ('USER', 'User'),
        ('AI', 'AI'),
    ]
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_system_data = models.BooleanField(default=False)
    data_payload = models.JSONField(null=True, blank=True, help_text="Rich structured data results (lists/dicts) returned by the query router")

    def __str__(self):
        return f"{self.sender}: {self.message[:50]}"

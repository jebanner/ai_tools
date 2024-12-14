from django.db import models
from wxcloudrun.apps.users.models import User

class EmotionRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emotion_records')
    emotion_type = models.CharField(max_length=50)
    emotion_level = models.IntegerField()
    description = models.TextField()
    ai_analysis = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'emotion_records'

    def __str__(self):
        return f"{self.user.username} - {self.emotion_type} - {self.created_at}" 
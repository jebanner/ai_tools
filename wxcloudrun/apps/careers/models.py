from django.db import models
from wxcloudrun.apps.users.models import User

class CareerRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='career_records')
    title = models.CharField(max_length=100)
    content = models.TextField()
    record_type = models.CharField(max_length=50)  # 记录类型(如:目标、计划、总结等)
    ai_analysis = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'career_records'

    def __str__(self):
        return f"{self.user.username} - {self.title} - {self.created_at}" 
from django.db import models
from wxcloudrun.apps.users.models import User

class Collection(models.Model):
    """智能收藏模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections', verbose_name='用户')
    title = models.CharField('标题', max_length=256)
    content = models.TextField('内容')
    url = models.URLField('原文链接', null=True, blank=True)
    summary = models.TextField('AI摘要', null=True, blank=True)
    tags = models.CharField('标签', max_length=512, null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'collections'
        ordering = ['-created_at']
        verbose_name = '智能收藏'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user.username} - {self.title}" 
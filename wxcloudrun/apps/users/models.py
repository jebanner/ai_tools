from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    """用户模型"""
    nickname = models.CharField('昵称', max_length=50, blank=True)
    avatar = models.URLField('头像', max_length=200, blank=True)
    openid = models.CharField('微信OpenID', max_length=100, unique=True)
    phone = models.CharField('手机号', max_length=11, blank=True)
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        
    def __str__(self):
        return self.nickname or self.username
        
class AIUsageStats(models.Model):
    """AI调用统计"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    api_name = models.CharField('API名称', max_length=128)
    call_date = models.DateField('调用日期', default=timezone.now)
    call_count = models.IntegerField('调用次数', default=0)
    success_count = models.IntegerField('成功次数', default=0)
    error_count = models.IntegerField('错误次数', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'ai_usage_stats'
        verbose_name = 'AI调用统计'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'api_name', 'call_date']
        
    def __str__(self):
        return f'{self.user.nickname}-{self.api_name}-{self.call_date}' 
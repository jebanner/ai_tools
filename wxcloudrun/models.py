from django.db import models

class Counters(models.Model):
    id = models.AutoField
    count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.count)

class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    nickname = models.CharField(max_length=50)
    password = models.CharField(max_length=128)  # 实际使用时应该哈希处理
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_users'  # 使用已有的表名

    def __str__(self):
        return self.username

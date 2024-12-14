from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, AIUsageStats

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """用户管理"""
    list_display = ['id', 'username', 'nickname', 'phone', 'is_staff', 'created_at']
    list_filter = ['is_staff', 'is_active']
    search_fields = ['username', 'nickname', 'phone']
    ordering = ['-id']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('扩展信息', {'fields': ('nickname', 'avatar', 'openid', 'phone')}),
    )
    
@admin.register(AIUsageStats)
class AIUsageStatsAdmin(admin.ModelAdmin):
    """AI调用统计管理"""
    list_display = ['id', 'user', 'api_name', 'call_date', 'call_count', 'success_count', 'error_count']
    list_filter = ['api_name', 'call_date']
    search_fields = ['user__username', 'user__nickname', 'api_name']
    ordering = ['-call_date', '-call_count'] 
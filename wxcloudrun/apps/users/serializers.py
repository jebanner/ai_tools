from rest_framework import serializers
from .models import User, AIUsageStats

class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'avatar', 'phone', 'created_at']
        read_only_fields = ['id', 'created_at']

class UserRegisterSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'password', 'nickname', 'openid']
        
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    """用户登录序列化器"""
    username = serializers.CharField()
    password = serializers.CharField()

class AIUsageStatsSerializer(serializers.ModelSerializer):
    """AI调用统计序列化器"""
    class Meta:
        model = AIUsageStats
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at'] 
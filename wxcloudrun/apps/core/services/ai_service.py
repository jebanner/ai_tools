import json
import logging
from django.conf import settings
from django.utils import timezone
from wxcloudrun.apps.users.models import AIUsageStats
from .coze_service import CozeService

logger = logging.getLogger('apps.core')

class AIService:
    """AI服务工具类"""
    
    def __init__(self, user):
        self.user = user
        self.coze = CozeService()
        
    def _check_usage_limit(self):
        """检查API调用限制"""
        today_calls = AIUsageStats.objects.filter(
            user=self.user,
            call_date=timezone.now().date()
        ).aggregate(
            total_calls=models.Sum('call_count')
        )['total_calls'] or 0
        
        if today_calls >= settings.COZE_SETTINGS['RATE_LIMIT_QPD']:
            raise Exception('已达到今日调用限制')
            
    def _update_stats(self, api_name, success=True):
        """更新API调用统计"""
        stats, _ = AIUsageStats.objects.get_or_create(
            user=self.user,
            api_name=api_name,
            call_date=timezone.now().date()
        )
        stats.call_count += 1
        if success:
            stats.success_count += 1
        else:
            stats.error_count += 1
        stats.save()
            
    def analyze_emotion(self, content):
        """情绪分析"""
        try:
            self._check_usage_limit()
            
            # 调用工作流进行情绪分析
            result = self.coze.run_workflow({
                'task_type': 'emotion',
                'content': content
            })
            
            self._update_stats('emotion_analysis', True)
            
            # 解析工作流返回结果
            output = json.loads(result.data)
            return {
                'emotion_type': output.get('emotion_type'),
                'emotion_level': output.get('emotion_level', 50),
                'analysis': output.get('analysis', ''),
                'image_url': output.get('image_url')
            }
            
        except Exception as e:
            self._update_stats('emotion_analysis', False)
            logger.error('情绪分析失败: %s', str(e), exc_info=True)
            return None
            
    def analyze_career(self, content, action_type=None, target_position=None):
        """职业发展分析"""
        try:
            self._check_usage_limit()
            
            # 调用工作流进行职业分析
            result = self.coze.run_workflow({
                'task_type': 'career',
                'content': content,
                'additional_params': {
                    'action_type': action_type,
                    'target_position': target_position
                }
            })
            
            self._update_stats('career_analysis', True)
            
            # 解析工作流返回结果
            output = json.loads(result.data)
            return {
                'suggestion': output.get('suggestion', ''),
                'skills': output.get('skills', []),
                'development_path': output.get('development_path', [])
            }
            
        except Exception as e:
            self._update_stats('career_analysis', False)
            logger.error('职业分析失败: %s', str(e), exc_info=True)
            return None
            
    def generate_summary(self, title, content, url=None):
        """生成内容摘要"""
        try:
            self._check_usage_limit()
            
            # 调用工作流生成摘要
            result = self.coze.run_workflow({
                'task_type': 'summary',
                'content': content,
                'additional_params': {
                    'title': title,
                    'url': url
                }
            })
            
            self._update_stats('content_summary', True)
            
            # 解析工作流返回结果
            output = json.loads(result.data)
            return {
                'summary': output.get('summary', ''),
                'tags': output.get('tags', []),
                'keywords': output.get('keywords', [])
            }
            
        except Exception as e:
            self._update_stats('content_summary', False)
            logger.error('生成摘要失败: %s', str(e), exc_info=True)
            return None
            
    def evaluate_ability(self, actions):
        """能力评估"""
        try:
            self._check_usage_limit()
            
            # 调用工作流进行能力评估
            result = self.coze.run_workflow({
                'task_type': 'ability',
                'content': json.dumps(actions)
            })
            
            self._update_stats('ability_evaluation', True)
            
            # 解析工作流返回结果
            output = json.loads(result.data)
            return {
                'overall_score': output.get('overall_score', 0),
                'skills': output.get('skills', []),
                'suggestions': output.get('suggestions', [])
            }
            
        except Exception as e:
            self._update_stats('ability_evaluation', False)
            logger.error('能力评估失败: %s', str(e), exc_info=True)
            return None 
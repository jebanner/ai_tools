from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch, MagicMock
from .models import EmotionRecord
from wxcloudrun.apps.core.services.coze_service import CozeService, CozeServiceError

User = get_user_model()

class EmotionRecordTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
    def test_create_emotion_record(self):
        """测试创建情绪记录"""
        record = EmotionRecord.objects.create(
            user=self.user,
            content='今天心情很好',
            emotion_level=8
        )
        
        self.assertEqual(record.user, self.user)
        self.assertEqual(record.content, '今天心情很好')
        self.assertEqual(record.emotion_level, 8)
        
class EmotionAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_generate_photo_success(self):
        """测试成功生成情绪照片"""
        with patch.object(CozeService, '_make_request') as mock_request:
            # 模拟COZE API响应
            mock_request.return_value = {
                'code': 200,
                'data': {
                    'photo_url': 'http://example.com/photo.jpg'
                }
            }
            
            url = reverse('emotion-generate-photo')
            data = {
                'text': '今天心情很好',
                'style': '写实风格'
            }
            
            response = self.client.post(url, data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('photo_url', response.data['data'])
            
    def test_generate_photo_no_text(self):
        """测试生成情绪照片时没有提供文本"""
        url = reverse('emotion-generate-photo')
        data = {'style': '写实风格'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_generate_photo_text_too_long(self):
        """测试生成情绪照片时文本过长"""
        url = reverse('emotion-generate-photo')
        data = {
            'text': 'x' * 501,
            'style': '写实风格'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_generate_photo_api_error(self):
        """测试生成情绪照片时API错误"""
        with patch.object(CozeService, '_make_request') as mock_request:
            mock_request.side_effect = CozeServiceError('API错误')
            
            url = reverse('emotion-generate-photo')
            data = {
                'text': '今天心情很好',
                'style': '写实风格'
            }
            
            response = self.client.post(url, data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def test_generate_curve_success(self):
        """测试成功生成情绪曲线"""
        with patch.object(CozeService, '_make_request') as mock_request:
            mock_request.return_value = {
                'code': 200,
                'data': {
                    'curve_url': 'http://example.com/curve.jpg',
                    'analysis': '情绪稳定'
                }
            }
            
            url = reverse('emotion-generate-curve')
            data = {
                'emotions': [
                    {'date': '2023-12-14', 'level': 8},
                    {'date': '2023-12-15', 'level': 7}
                ]
            }
            
            response = self.client.post(url, data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('curve_url', response.data['data'])
            self.assertIn('analysis', response.data['data'])
            
    def test_statistics_success(self):
        """测试成功获取统计数据"""
        # 创建测试数据
        EmotionRecord.objects.create(
            user=self.user,
            content='测试1',
            emotion_level=8
        )
        EmotionRecord.objects.create(
            user=self.user,
            content='测试2',
            emotion_level=6
        )
        
        url = reverse('emotion-statistics')
        params = {
            'start_date': '2023-12-01',
            'end_date': '2023-12-31'
        }
        
        response = self.client.get(url, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['total_count'], 2)
        self.assertEqual(response.data['data']['average_level'], 7.0)
        
    def test_statistics_invalid_date_format(self):
        """测试统计数据时日期格式错误"""
        url = reverse('emotion-statistics')
        params = {
            'start_date': '2023/12/01',
            'end_date': '2023/12/31'
        }
        
        response = self.client.get(url, params)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_statistics_date_range_too_large(self):
        """测试统计数据时日期范围过大"""
        url = reverse('emotion-statistics')
        params = {
            'start_date': '2023-01-01',
            'end_date': '2023-12-31'
        }
        
        response = self.client.get(url, params)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 
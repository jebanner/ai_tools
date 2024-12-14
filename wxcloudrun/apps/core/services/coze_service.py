import os
import time
import json
import requests
from typing import Optional, Dict, Any
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from django.conf import settings
import base64
import logging
from requests.exceptions import RequestException
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class CozeServiceError(Exception):
    """COZE 服务异常"""
    pass

class CozeService:
    def __init__(self):
        self.base_url = settings.COZE_API_BASE_URL
        self.app_id = settings.COZE_APP_ID
        self.private_key_path = settings.COZE_PRIVATE_KEY_PATH
        self.public_key_fingerprint = settings.COZE_PUBLIC_KEY_FINGERPRINT
        self.timeout = getattr(settings, 'COZE_API_TIMEOUT', 30)
        self.private_key: Optional[RSAPrivateKey] = None
        self._load_private_key()

    def _load_private_key(self) -> None:
        """加载私钥"""
        try:
            if not os.path.exists(self.private_key_path):
                raise CozeServiceError(f"私钥文件不存在: {self.private_key_path}")
                
            with open(self.private_key_path, 'rb') as key_file:
                self.private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None
                )
        except Exception as e:
            logger.error(f"加载私钥失败: {str(e)}")
            raise CozeServiceError(f"加载私钥失败: {str(e)}")

    def _generate_signature(self, data: Dict[str, Any]) -> str:
        """生成请求签名"""
        try:
            if not self.private_key:
                raise CozeServiceError("私钥未加载")
                
            # 将数据转换为字符串并编码
            message = json.dumps(data, sort_keys=True).encode()
            
            # 使用私钥签名
            signature = self.private_key.sign(
                message,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            
            # 返回 base64 编码的签名
            return base64.b64encode(signature).decode()
        except Exception as e:
            logger.error(f"生成签名失败: {str(e)}")
            raise CozeServiceError(f"生成签名失败: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=lambda e: isinstance(e, (RequestException, CozeServiceError))
    )
    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """发送请求到 COZE API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            # 添加时间戳和应用ID
            data['timestamp'] = int(time.time())
            data['app_id'] = self.app_id
            
            # 生成签名
            signature = self._generate_signature(data)
            
            # 设置请求头
            headers = {
                'Content-Type': 'application/json',
                'X-Public-Key-Fingerprint': self.public_key_fingerprint,
                'X-Signature': signature
            }
            
            # 发送请求
            response = requests.post(
                url,
                json=data,
                headers=headers,
                timeout=self.timeout
            )
            
            # 检查响应状态码
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            
            # 检查业务状态码
            if result.get('code') != 200:
                raise CozeServiceError(
                    f"业务处理失败: {result.get('message', '未知错误')}"
                )
                
            return result
            
        except requests.exceptions.Timeout:
            logger.error(f"请求超时: {url}")
            raise CozeServiceError("请求超时")
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {str(e)}")
            raise CozeServiceError(f"请求失败: {str(e)}")
        except json.JSONDecodeError:
            logger.error("响应解析失败")
            raise CozeServiceError("响应解析失败")
        except Exception as e:
            logger.error(f"未知错误: {str(e)}")
            raise CozeServiceError(f"未知错误: {str(e)}")

    def generate_emotion_photo(self, text: str, style: Optional[str] = None) -> Dict[str, Any]:
        """生成情绪照片"""
        if not text:
            raise ValueError("文本内容不能为空")
            
        data = {
            'workflow_id': settings.COZE_EMOTION_PHOTO_WORKFLOW_ID,
            'inputs': {
                'text': text,
                'style': style or '写实风格'
            }
        }
        return self._make_request('/workflow/invoke', data)

    def generate_emotion_curve(self, emotions: list) -> Dict[str, Any]:
        """生成情绪曲线"""
        if not emotions:
            raise ValueError("情绪数据不能为空")
            
        data = {
            'workflow_id': settings.COZE_EMOTION_CURVE_WORKFLOW_ID,
            'inputs': {
                'emotions': emotions
            }
        }
        return self._make_request('/workflow/invoke', data)

    def generate_career_action(self, description: str) -> Dict[str, Any]:
        """生成职业行动建议"""
        if not description:
            raise ValueError("描述内容不能为空")
            
        data = {
            'workflow_id': settings.COZE_CAREER_ACTION_WORKFLOW_ID,
            'inputs': {
                'description': description
            }
        }
        return self._make_request('/workflow/invoke', data)

    def generate_career_ability(self, experience: str) -> Dict[str, Any]:
        """生成能力画像"""
        if not experience:
            raise ValueError("经历描述不能为空")
            
        data = {
            'workflow_id': settings.COZE_CAREER_ABILITY_WORKFLOW_ID,
            'inputs': {
                'experience': experience
            }
        }
        return self._make_request('/workflow/invoke', data)

    def generate_collection_summary(self, content: str) -> Dict[str, Any]:
        """生成智能摘要"""
        if not content:
            raise ValueError("内容不能为空")
            
        data = {
            'workflow_id': settings.COZE_COLLECTION_SUMMARY_WORKFLOW_ID,
            'inputs': {
                'content': content
            }
        }
        return self._make_request('/workflow/invoke', data)

# 创建服务实例
coze_service = CozeService()
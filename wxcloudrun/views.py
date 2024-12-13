import json
import logging
from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render
from wxcloudrun.models import Counters, User

logger = logging.getLogger('log')

def index(request, _):
    """获取主页"""
    return render(request, 'index.html')

def counter(request, _):
    """统一处理 /api/count 的请求"""
    rsp = JsonResponse({'code': -1, 'errorMsg': '请求方式错误'}, json_dumps_params={'ensure_ascii': False})
    
    if request.method == 'GET':
        rsp = get_count()
    elif request.method == 'POST':
        rsp = handle_post_request(request)
    
    logger.info('response result: {}'.format(rsp.content.decode('utf-8')))
    return rsp

def handle_post_request(request):
    """处理 POST 请求"""
    try:
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        logger.info('request body: {}'.format(body))

        if 'action' not in body:
            return JsonResponse({'code': -1, 'errorMsg': '缺少action参数'}, json_dumps_params={'ensure_ascii': False})

        # 根据 action 分发到不同的处理函数
        action_handlers = {
            'inc': handle_counter_inc,
            'clear': handle_counter_clear,
            'user_register': handle_user_register,
            'user_login': handle_user_login,
            'get_user_info': handle_get_user_info,
            'update_user_info': handle_update_user_info
        }

        handler = action_handlers.get(body['action'])
        if handler:
            return handler(body)
        else:
            return JsonResponse({'code': -1, 'errorMsg': 'action参数错误'}, json_dumps_params={'ensure_ascii': False})

    except json.JSONDecodeError:
        logger.error('Invalid JSON data')
        return JsonResponse({'code': -1, 'errorMsg': '无效的请求数据'}, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        logger.error('Error processing request: {}'.format(str(e)))
        return JsonResponse({'code': -1, 'errorMsg': '服务器内部错误'}, json_dumps_params={'ensure_ascii': False})

def get_count():
    """获取当前计数"""
    try:
        data = Counters.objects.get(id=1)
        return JsonResponse({'code': 0, 'data': data.count}, json_dumps_params={'ensure_ascii': False})
    except Counters.DoesNotExist:
        return JsonResponse({'code': 0, 'data': 0}, json_dumps_params={'ensure_ascii': False})

def handle_counter_inc(body):
    """处理计数器自增"""
    try:
        data = Counters.objects.get(id=1)
    except Counters.DoesNotExist:
        data = Counters()
        data.id = 1
        data.count = 0
    
    data.count += 1
    data.save()
    return JsonResponse({'code': 0, 'data': data.count}, json_dumps_params={'ensure_ascii': False})

def handle_counter_clear(body):
    """处理计数器清零"""
    try:
        data = Counters.objects.get(id=1)
        data.delete()
    except Counters.DoesNotExist:
        logger.info('record not exist')
    return JsonResponse({'code': 0, 'data': 0}, json_dumps_params={'ensure_ascii': False})

def handle_user_register(body):
    """处理用户注册"""
    try:
        username = body.get('username')
        nickname = body.get('nickname')
        password = body.get('password')
        
        logger.info('Processing registration for username: {}'.format(username))
        
        # 验证必填字段
        if not all([username, nickname, password]):
            return JsonResponse({'code': -1, 'errorMsg': '缺少必要的注册信息'}, json_dumps_params={'ensure_ascii': False})
            
        # 检查用户名是否已存在
        if User.objects.filter(username=username).exists():
            return JsonResponse({'code': -1, 'errorMsg': '用户名已存在'}, json_dumps_params={'ensure_ascii': False})
            
        # 创建新用户
        user = User.objects.create(
            username=username,
            nickname=nickname,
            password=password,  # 实际使用时应该哈希处理
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        return JsonResponse({
            'code': 0,
            'data': {
                'id': user.id,
                'username': user.username,
                'nickname': user.nickname
            }
        }, json_dumps_params={'ensure_ascii': False})
        
    except Exception as e:
        logger.error('Registration error: {}'.format(str(e)))
        return JsonResponse({'code': -1, 'errorMsg': '注册失败，请稍后重试'}, json_dumps_params={'ensure_ascii': False})

def handle_user_login(body):
    """处理用户登录"""
    try:
        username = body.get('username')
        password = body.get('password')
        
        logger.info('Processing login for username: {}'.format(username))
        
        # 验证必填字段
        if not all([username, password]):
            return JsonResponse({'code': -1, 'errorMsg': '请输入用户名和密码'}, json_dumps_params={'ensure_ascii': False})
            
        # 验证用户
        try:
            user = User.objects.get(username=username)
            if user.password == password:  # 实际使用时应该哈希比对
                return JsonResponse({
                    'code': 0,
                    'data': {
                        'id': user.id,
                        'username': user.username,
                        'nickname': user.nickname
                    }
                }, json_dumps_params={'ensure_ascii': False})
            else:
                return JsonResponse({'code': -1, 'errorMsg': '密码错误'}, json_dumps_params={'ensure_ascii': False})
        except User.DoesNotExist:
            return JsonResponse({'code': -1, 'errorMsg': '用户不存在'}, json_dumps_params={'ensure_ascii': False})
            
    except Exception as e:
        logger.error('Login error: {}'.format(str(e)))
        return JsonResponse({'code': -1, 'errorMsg': '登录失败，请稍后重试'}, json_dumps_params={'ensure_ascii': False})

def handle_get_user_info(body):
    """处理获取用户信息"""
    try:
        user_id = body.get('user_id')
        
        if not user_id:
            return JsonResponse({'code': -1, 'errorMsg': '缺少用户ID'}, json_dumps_params={'ensure_ascii': False})
            
        try:
            user = User.objects.get(id=user_id)
            return JsonResponse({
                'code': 0,
                'data': {
                    'id': user.id,
                    'username': user.username,
                    'nickname': user.nickname
                }
            }, json_dumps_params={'ensure_ascii': False})
        except User.DoesNotExist:
            return JsonResponse({'code': -1, 'errorMsg': '用户不存在'}, json_dumps_params={'ensure_ascii': False})
            
    except Exception as e:
        logger.error('Get user info error: {}'.format(str(e)))
        return JsonResponse({'code': -1, 'errorMsg': '获取用户信息失败'}, json_dumps_params={'ensure_ascii': False})

def handle_update_user_info(body):
    """处理更新用户信息"""
    try:
        user_id = body.get('user_id')
        nickname = body.get('nickname')
        
        if not all([user_id, nickname]):
            return JsonResponse({'code': -1, 'errorMsg': '缺少必要的更新信息'}, json_dumps_params={'ensure_ascii': False})
            
        try:
            user = User.objects.get(id=user_id)
            user.nickname = nickname
            user.updated_at = datetime.now()
            user.save()
            
            return JsonResponse({
                'code': 0,
                'data': {
                    'id': user.id,
                    'username': user.username,
                    'nickname': user.nickname
                }
            }, json_dumps_params={'ensure_ascii': False})
        except User.DoesNotExist:
            return JsonResponse({'code': -1, 'errorMsg': '用户不存在'}, json_dumps_params={'ensure_ascii': False})
            
    except Exception as e:
        logger.error('Update user info error: {}'.format(str(e)))
        return JsonResponse({'code': -1, 'errorMsg': '更新用户信息失败'}, json_dumps_params={'ensure_ascii': False})

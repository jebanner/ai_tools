import json
import logging
from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from wxcloudrun.models import Counters, User

logger = logging.getLogger('log')

__all__ = ['index', 'counter', 'user_register', 'user_login', 'user_info']


def index(request):
    """获取主页"""
    return render(request, 'index.html')


@csrf_exempt
def user_register(request):
    """用户注册"""
    if request.method != 'POST':
        return JsonResponse({
            'code': -1,
            'errorMsg': '不支持的请求方法'
        }, json_dumps_params={'ensure_ascii': False})

    try:
        body = json.loads(request.body.decode('utf-8'))
        username = body.get('username')
        nickname = body.get('nickname')
        password = body.get('password')

        logger.info('Processing registration for username: {}'.format(username))

        # 验证必填字段
        if not all([username, nickname, password]):
            return JsonResponse({
                'code': -1,
                'errorMsg': '缺少必要的注册信息'
            }, json_dumps_params={'ensure_ascii': False})

        # 检查用户名是否已存在
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'code': -1,
                'errorMsg': '用户名已存在'
            }, json_dumps_params={'ensure_ascii': False})

        # 创建新用户
        user = User.objects.create(
            username=username,
            nickname=nickname,
            password=password,  # 实际使用时应该哈希处理
            role='user',
            daily_limit=20
        )

        return JsonResponse({
            'code': 0,
            'data': {
                'id': user.id,
                'username': user.username,
                'nickname': user.nickname,
                'role': 'user',
                'daily_limit': 20
            }
        }, json_dumps_params={'ensure_ascii': False})

    except json.JSONDecodeError:
        logger.error('Invalid JSON data')
        return JsonResponse({
            'code': -1,
            'errorMsg': '无效的请求数据'
        }, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        logger.error('Registration error: {}'.format(str(e)))
        return JsonResponse({
            'code': -1,
            'errorMsg': '注册失败，请稍后重试'
        }, json_dumps_params={'ensure_ascii': False})


@csrf_exempt
def user_login(request):
    """用户登录"""
    if request.method != 'POST':
        return JsonResponse({
            'code': -1,
            'errorMsg': '不支持的请求方法'
        }, json_dumps_params={'ensure_ascii': False})

    try:
        body = json.loads(request.body.decode('utf-8'))
        username = body.get('username')
        password = body.get('password')

        logger.info('Processing login for username: {}'.format(username))

        # 验证必填字段
        if not all([username, password]):
            return JsonResponse({
                'code': -1,
                'errorMsg': '请输入用户名和密码'
            }, json_dumps_params={'ensure_ascii': False})

        # 验证用户
        try:
            user = User.objects.get(username=username)
            if user.password == password:  # 实际使用时应该哈希比对
                # 生成简单的token
                token = f"{user.id}:{datetime.now().timestamp()}"

                # 更新用户token
                user.token = token
                user.save()

                return JsonResponse({
                    'code': 0,
                    'data': {
                        'token': token,
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'nickname': user.nickname,
                            'role': user.role,
                            'daily_limit': user.daily_limit
                        }
                    }
                }, json_dumps_params={'ensure_ascii': False})
            else:
                return JsonResponse({
                    'code': -1,
                    'errorMsg': '密码错误'
                }, json_dumps_params={'ensure_ascii': False})
        except User.DoesNotExist:
            return JsonResponse({
                'code': -1,
                'errorMsg': '用户不存在'
            }, json_dumps_params={'ensure_ascii': False})

    except json.JSONDecodeError:
        logger.error('Invalid JSON data')
        return JsonResponse({
            'code': -1,
            'errorMsg': '无效的请求数据'
        }, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        logger.error('Login error: {}'.format(str(e)))
        return JsonResponse({
            'code': -1,
            'errorMsg': '登录失败，请稍后重试'
        }, json_dumps_params={'ensure_ascii': False})


@csrf_exempt
def user_info(request):
    """获取用户信息"""
    if request.method != 'GET':
        return JsonResponse({
            'code': -1,
            'errorMsg': '不支持的请求方法'
        }, json_dumps_params={'ensure_ascii': False})

    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')

        if not token:
            return JsonResponse({
                'code': -1,
                'errorMsg': '未登录'
            }, json_dumps_params={'ensure_ascii': False})

        try:
            user = User.objects.get(token=token)
            return JsonResponse({
                'code': 0,
                'data': {
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'nickname': user.nickname,
                        'role': user.role,
                        'daily_limit': user.daily_limit
                    }
                }
            }, json_dumps_params={'ensure_ascii': False})
        except User.DoesNotExist:
            return JsonResponse({
                'code': -1,
                'errorMsg': '登录已过期'
            }, json_dumps_params={'ensure_ascii': False})

    except Exception as e:
        logger.error('Get user info error: {}'.format(str(e)))
        return JsonResponse({
            'code': -1,
            'errorMsg': '获取用户信息失败'
        }, json_dumps_params={'ensure_ascii': False})


@csrf_exempt
def counter(request):
    """处理计数器请求"""
    if request.method == 'GET':
        rsp = get_count()
    else:
        rsp = handle_counter_inc(request)

    return rsp


def get_count():
    """获取当前计数"""
    try:
        data = Counters.objects.get(id=1)
        return JsonResponse({'code': 0, 'data': data.count}, json_dumps_params={'ensure_ascii': False})
    except Counters.DoesNotExist:
        return JsonResponse({'code': 0, 'data': 0}, json_dumps_params={'ensure_ascii': False})


def handle_counter_inc(request):
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

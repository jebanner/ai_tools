import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from wxcloudrun.models import Counters

logger = logging.getLogger('log')

@csrf_exempt
def counter(request):
    """计数器接口"""
    if request.method == 'GET':
        rsp = JsonResponse({'code': 0, 'errorMsg': ''}, json_dumps_params={'ensure_ascii': False})
        try:
            counter = Counters.objects.get(id=1)
            rsp = JsonResponse({
                'code': 0,
                'errorMsg': '',
                'data': counter.count
            }, json_dumps_params={'ensure_ascii': False})
        except Counters.DoesNotExist:
            Counters.objects.create(id=1, count=0)
            rsp = JsonResponse({
                'code': 0,
                'errorMsg': '',
                'data': 0
            }, json_dumps_params={'ensure_ascii': False})
        return rsp
    elif request.method == 'POST':
        rsp = JsonResponse({'code': 0, 'errorMsg': ''}, json_dumps_params={'ensure_ascii': False})
        try:
            body = json.loads(request.body)
            action = body.get('action')
            counter = Counters.objects.get(id=1) if Counters.objects.filter(id=1).exists() else Counters.objects.create(id=1, count=0)
            
            if action == 'inc':
                counter.count += 1
            elif action == 'clear':
                counter.count = 0
            counter.save()

            rsp = JsonResponse({
                'code': 0,
                'errorMsg': '',
                'data': counter.count,
            }, json_dumps_params={'ensure_ascii': False})
        except Exception as e:
            logger.error('counter api error: %s' % e)
            rsp = JsonResponse({
                'code': -1,
                'errorMsg': str(e)
            }, json_dumps_params={'ensure_ascii': False})
        return rsp
    else:
        rsp = JsonResponse({
            'code': -1,
            'errorMsg': 'method not allowed'
        }, json_dumps_params={'ensure_ascii': False})
        return rsp

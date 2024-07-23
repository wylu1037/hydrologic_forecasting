# Create your views here.
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from app.request import HandleMapRequest, CreateProjectRequest, ModelForecastRequest, HandleStationRequest, \
    ExportMapRequest, ExportStationRequest
from app.service.app_service import AppService

service = AppService()


def request_to_object(request, clazz):
    """
    通过json字符串实例化一个类

    Args:
        request
        clazz

    Returns:
        class
    """
    json_string = request.body.decode('utf-8')
    json_data = json.loads(json_string)
    return clazz(**json_data)


@csrf_exempt
def handle_map_controller(request):
    if request.method == 'GET':
        return JsonResponse({'code': -1, 'error': 'Unsupported method'})
    try:
        req = request_to_object(request, HandleMapRequest)
        service.handle_map(req)
    except Exception as e:
        return JsonResponse({'code': -1, 'error': str(e)})
    else:
        return JsonResponse({'code': 0})


@csrf_exempt
def handle_station_controller(request):
    if request.method == 'GET':
        return JsonResponse({'code': -1, 'error': 'Unsupported method'})
    try:
        req = request_to_object(request, HandleStationRequest)
        service.handle_station()
    except Exception as e:
        return JsonResponse({'code': -1, 'error': str(e)})
    else:
        return JsonResponse({'code': 0})


@csrf_exempt
def execute(request):
    if request.method == 'GET':
        return JsonResponse({'code': -1, 'error': 'Unsupported method'})
    try:
        req = request_to_object(request, ModelForecastRequest)
        result = AppService.run(req)
    except Exception as e:
        return JsonResponse({'code': -1, 'error': str(e)})
    else:
        return JsonResponse({'code': 0, 'data': result})


# 创建项目
@csrf_exempt
def create_project(request):
    if request.method == 'GET':
        return JsonResponse({'code': -1, 'error': 'Unsupported method'})
    try:
        req = request_to_object(request, CreateProjectRequest)
        primary_key = AppService.create_project(req)
    except Exception as e:
        return JsonResponse({'code': -1, 'error': str(e)})
    else:
        return JsonResponse({'code': 0, 'data': primary_key})


@csrf_exempt
def export_map_controller(request):
    if request.method == 'GET':
        return JsonResponse({'code': -1, 'error': 'Unsupported method'})
    try:
        req = request_to_object(request, ExportMapRequest)
        data = service.export_map(req)
    except Exception as e:
        return JsonResponse({'code': -1, 'error': str(e)})
    else:
        return JsonResponse({'code': 0, 'data': data})


@csrf_exempt
def export_station_controller(request):
    if request.method == 'GET':
        return JsonResponse({'code': -1, 'error': 'Unsupported method'})
    try:
        req = request_to_object(request, ExportStationRequest)
        data = service.export_station(req)
    except Exception as e:
        return JsonResponse({'code': -1, 'error': str(e)})
    else:
        return JsonResponse({'code': 0, 'data': data})


@csrf_exempt
def project_pagination(request, page, size):
    if request.method == 'POST':
        return JsonResponse({'code': -1, 'error': 'Unsupported method'})
    try:
        data = service.project_pagination(page, size)
        print(data)
    except Exception as e:
        return JsonResponse({'code': -1, 'error': str(e)})
    else:
        return JsonResponse({'code': 0, 'data': data})

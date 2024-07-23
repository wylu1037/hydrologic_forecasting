# Create your views here.
import json
from dataclasses import asdict

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from app.request import HandleMapRequest, CreateProjectRequest, ModelForecastRequest, HandleStationRequest, \
    ExportMapRequest, ExportStationRequest
from app.service.app_service import AppService

service = AppService()


@csrf_exempt
def handle_map_controller(request):
    if request.method == 'GET':
        return JsonResponse({'error': 'Unsupported method'})
    try:
        req = request_to_object(request, HandleMapRequest)
        service.handle_map(req)
    except Exception as e:
        return JsonResponse({'error': str(e)})
    else:
        return JsonResponse({'status': 'ok'})


@csrf_exempt
def handle_station_controller(request):
    if request.method == 'GET':
        return JsonResponse({'error': 'Unsupported method'})
    try:
        req = request_to_object(request, HandleStationRequest)
        service.handle_station()
    except Exception as e:
        return JsonResponse({'error': str(e)})
    else:
        return JsonResponse({'status': 'ok'})


@csrf_exempt
def execute(request):
    if request.method == 'GET':
        return JsonResponse({'error': 'Unsupported method'})
    try:
        req = request_to_object(request, ModelForecastRequest)
        result = AppService.run(req)
    except Exception as e:
        return JsonResponse({'error': str(e)})
    else:
        return JsonResponse({'status': 'ok', 'data': result})


# 创建项目
@csrf_exempt
def create_project(request):
    if request.method == 'GET':
        return JsonResponse({'error': 'Unsupported method'})
    try:
        req = request_to_object(request, CreateProjectRequest)
        primary_key = AppService.create_project(req)
    except Exception as e:
        return JsonResponse({'error': str(e)})
    else:
        return JsonResponse({'status': 'ok', 'data': primary_key})


@csrf_exempt
def export_map(request):
    if request.method == 'GET':
        return JsonResponse({'error': 'Unsupported method'})
    try:
        req = request_to_object(request, ExportMapRequest)
    except Exception as e:
        return JsonResponse({'error': str(e)})
    else:
        return JsonResponse({'status': 'ok', 'data': asdict(req)})


@csrf_exempt
def export_station(request):
    if request.method == 'GET':
        return JsonResponse({'error': 'Unsupported method'})
    try:
        req = request_to_object(request, ExportStationRequest)
        print(req)
    except Exception as e:
        return JsonResponse({'error': str(e)})
    else:
        return JsonResponse({'status': 'ok', 'data': asdict(req)})


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

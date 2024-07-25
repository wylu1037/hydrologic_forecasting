# Create your views here.
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from app.request import HandleMapRequest, RunProjectRequest, HandleStationRequest, \
    ExportMapRequest, ExportStationRequest, UpdateProjectRequest
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
def ping_controller(request):
    return JsonResponse({'reply': '🎉🎉🎉 Congratulations! Success visited.'})


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
        service.handle_station(req)
    except Exception as e:
        return JsonResponse({'code': -1, 'error': str(e)})
    else:
        return JsonResponse({'code': 0})


@csrf_exempt
def run_project(request):
    """
    创建项目，并运行模型
    """
    if request.method == 'GET':
        return JsonResponse({'code': -1, 'error': 'Unsupported method'})
    try:
        req = request_to_object(request, RunProjectRequest)
        primary_key = service.run_project(req)
    except Exception as e:
        return JsonResponse({'code': -1, 'error': str(e)})
    else:
        return JsonResponse({'code': 0, 'data': primary_key})


@csrf_exempt
def update_project(request):
    """
    更新项目
    """
    if request.method == 'GET':
        return JsonResponse({'code': -1, 'error': 'Unsupported method'})
    try:
        req = request_to_object(request, UpdateProjectRequest)
        service.update_project(req)
    except Exception as e:
        return JsonResponse({'code': -1, 'error': str(e)})
    else:
        return JsonResponse({'code': 0})


@csrf_exempt
def delete_project(request, project_id):
    """
    删除项目信息
    """
    if request.method == 'GET':
        return JsonResponse({'code': -1, 'error': 'Unsupported method'})
    try:
        service.delete_project(project_id)
    except Exception as e:
        return JsonResponse({'code': -1, 'error': str(e)})
    else:
        return JsonResponse({'code': 0})


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
    except Exception as e:
        return JsonResponse({'code': -1, 'error': str(e)})
    else:
        return JsonResponse({'code': 0, 'data': data})


@csrf_exempt
def representation_station_controller(request):
    if request.method == 'GET':
        return JsonResponse({'code': -1, 'error': 'Unsupported method'})
    try:
        data = service.representation_station()
    except Exception as e:
        return JsonResponse({'code': -1, 'error': str(e)})
    else:
        return JsonResponse({'code': 0, 'data': data})


@csrf_exempt
def trend_station_controller(request, name):
    if request.method == 'GET':
        return JsonResponse({'code': -1, 'error': 'Unsupported method'})
    try:
        data = service.trend_station(name)
    except Exception as e:
        return JsonResponse({'code': -1, 'error': str(e)})
    else:
        return JsonResponse({'code': 0, 'data': data})


@csrf_exempt
def latest_water_information(request):
    if request.method == 'GET':
        return JsonResponse({'code': -1, 'error': 'Unsupported method'})
    try:
        data = service.latest_water_information()
    except Exception as e:
        return JsonResponse({'code': -1, 'error': str(e)})
    else:
        return JsonResponse({'code': 0, 'data': data})

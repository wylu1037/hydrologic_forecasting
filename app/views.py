# Create your views here.
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from app.request import ModelForecastRequest, HandleMapRequest, CreateProjectRequest
from app.service.mapping_service import MappingService
from app.service.scripts_service import ScriptsService


@csrf_exempt
def handle_map_controller(request):
    if request.method == 'GET':
        return JsonResponse({'error': 'Unsupported method'})
    try:
        body = json.loads(request.body.decode('utf-8'))
        req = HandleMapRequest(project_id=body['project_id'])

        if 'time_index' in body and body['time_index'] >= 0:
            req.time_index = body['time_index']
        if 'min_water_depth' in body and body['min_water_depth'] > 0:
            req.min_water_depth = body['min_water_depth']
        MappingService.handle_map(req)
    except Exception as e:
        return JsonResponse({'error': str(e)})
    else:
        return JsonResponse({'status': 'ok'})


@csrf_exempt
def handle_station_controller(request):
    if request.method == 'GET':
        return JsonResponse({'error': 'Unsupported method'})
    try:
        body = json.loads(request.body.decode('utf-8'))
        MappingService.handle_station()
    except Exception as e:
        return JsonResponse({'error': str(e)})
    else:
        return JsonResponse({'status': 'ok'})


@csrf_exempt
def execute(request):
    if request.method == 'GET':
        return JsonResponse({'error': 'Unsupported method'})
    try:
        body = json.loads(request.body.decode('utf-8'))
        req = ModelForecastRequest(body['scheme_name'], body['date_time'], body['step_size'], body['schem_description'],
                                   body['args'])
        result = ScriptsService.run(req)
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
        body = json.loads(request.body.decode('utf-8'))
        req = CreateProjectRequest(body['name'], body['description'], body['time_index'])
        primary_key = MappingService.create_project(req)
    except Exception as e:
        return JsonResponse({'error': str(e)})
    else:
        return JsonResponse({'status': 'ok', 'data': primary_key})

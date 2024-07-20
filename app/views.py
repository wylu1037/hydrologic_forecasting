# Create your views here.
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from app.request import ModelForecastRequest, ConvertNcRequest, CreateProjectRequest, ImportWaterInformationRequest, \
    WaterInformationListRequest
from app.service.mapping_service import MappingService
from app.service.scripts_service import ScriptsService


@csrf_exempt
def convert_nc_to_shp_controller(request):
    if request.method == 'GET':
        return JsonResponse({'error': 'Unsupported method'})
    try:
        body = json.loads(request.body.decode('utf-8'))
        req = ConvertNcRequest(project_id=body['project_id'])
        if hasattr(request, 'time_index') and request['time_index'] > 0:
            req.time_index = body['time_index']
        if hasattr(request, 'min_water_depth') and body['min_water_depth'] > 0:
            req.min_water_depth = body['min_water_depth']
        MappingService.convert_nc_to_shp(req)
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


@csrf_exempt
def import_water_information(request):
    if request.method == 'GET':
        return JsonResponse({'error': 'Unsupported method'})
    try:
        body = json.loads(request.body.decode('utf-8'))
        req = ImportWaterInformationRequest(station=body['station'], datetime=body['datetime'],
                                            upstream_water_level=body['upstream_water_level'],
                                            downstream_water_level=body['downstream_water_level'],
                                            flow=body['flow'])
        pk = MappingService.import_water_information(req)
    except Exception as e:
        return JsonResponse({'error': str(e)})
    else:
        return JsonResponse({'status': 'ok', 'data': pk})


@csrf_exempt
def water_information_list(request):
    if request.method == 'GET':
        return JsonResponse({'error': 'Unsupported method'})
    try:
        body = json.loads(request.body.decode('utf-8'))
        req = WaterInformationListRequest(
            station=body['station'],
            start_datetime=body['start_datetime'],
            end_datetime=body['end_datetime'],
        )
        data = MappingService.water_information_list(req)
    except Exception as e:
        return JsonResponse({'error': str(e)})
    else:
        return JsonResponse({'status': 'ok', 'data': list(data)})

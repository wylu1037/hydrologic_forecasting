# Create your views here.
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from app.request import ModelForecastRequest
from app.service.mapping_service import MappingService
from app.service.scripts_service import ScriptsService


def convert_nc_to_shp_controller(request):
    try:
        MappingService.convert_nc_to_shp()
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

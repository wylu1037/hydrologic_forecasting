# Create your views here.
from django.http import JsonResponse

import tools.scripts
from app.service.mapping_service import MappingService


def convert_nc_to_shp_controller(request):
    try:
        MappingService.convert_nc_to_shp()
    except Exception as e:
        return JsonResponse({'error': str(e)})
    else:
        return JsonResponse({'status': 'ok'})


def execute(request):
    try:
        arg1 = request.GET["arg1"]
        arg2 = request.GET["arg2"]
        result = tools.scripts.run([arg1, arg2])
    except Exception as e:
        return JsonResponse({'error': str(e)})
    else:
        return JsonResponse({'status': 'ok', 'data': result})

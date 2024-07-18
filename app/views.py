# Create your views here.
from django.http import JsonResponse

from app.service.mapping_service import MappingService


def convert_nc_to_shp_controller(request):
    try:
        MappingService.convert_nc_to_shp()
    except Exception as e:
        return JsonResponse({'error': str(e)})
    else:
        return JsonResponse({'status': 'ok'})

# Create your views here.
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view

from app.request import HandleMapRequest, RunProjectRequest, HandleStationRequest, \
    ExportMapRequest, ExportStationRequest, UpdateProjectRequest, ExportHistoryStationRequest
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
    if json_string == '':
        json_string = '{}'
    json_data = json.loads(json_string)
    return clazz(**json_data)


@extend_schema(
    summary="Ping接口",
)
@api_view(['GET'])
@csrf_exempt
def ping_controller(request):
    return JsonResponse({'reply': '🎉🎉🎉 Congratulations! Success visited.'})


@extend_schema(
    summary="处理模型输出的网格文件",
)
@api_view(['POST'])
@csrf_exempt
def handle_map_controller(request):
    try:
        req = request_to_object(request, HandleMapRequest)
        service.handle_map(req)
    except Exception as e:
        return JsonResponse({'code': -1, 'error': str(e)})
    else:
        return JsonResponse({'code': 0})


@extend_schema(
    summary="处理模型输出的站点文件",
)
@api_view(['POST'])
@csrf_exempt
def handle_station_controller(request):
    try:
        req = request_to_object(request, HandleStationRequest)
        service.handle_station(req)
    except Exception as e:
        return JsonResponse({'code': -1, 'error': str(e)})
    else:
        return JsonResponse({'code': 0})


@extend_schema(
    summary="创建方案，并且运行模型",
)
@api_view(['POST'])
@csrf_exempt
def run_project_controller(request):
    """
    创建项目，并运行模型
    """
    try:
        req = request_to_object(request, RunProjectRequest)
        primary_key = service.run_project(req)
    except Exception as e:
        return JsonResponse({'code': -1, 'error': str(e)})
    else:
        return JsonResponse({'code': 0, 'data': primary_key})


@extend_schema(
    summary="方案列表",
)
@api_view(['GET'])
@csrf_exempt
def project_list_controller(request):
    try:
        data = service.project_list()
    except Exception as e:
        return JsonResponse({'code': -1, 'error': str(e)})
    else:
        return JsonResponse({'code': 0, 'data': data})


@extend_schema(
    summary="更新方案",
)
@api_view(['POST'])
@csrf_exempt
def update_project_controller(request):
    """
    更新项目
    """
    try:
        req = request_to_object(request, UpdateProjectRequest)
        service.update_project(req)
    except Exception as e:
        return JsonResponse({'code': -1, 'error': str(e)})
    else:
        return JsonResponse({'code': 0})


@extend_schema(
    summary="删除方案",
)
@api_view(['POST'])
@csrf_exempt
def delete_project_controller(request, project_id):
    """
    删除项目信息
    """
    try:
        service.delete_project(project_id)
    except Exception as e:
        return JsonResponse({'code': -1, 'error': str(e)})
    else:
        return JsonResponse({'code': 0})


@extend_schema(
    summary="查询网格数据",
)
@api_view(['POST'])
@csrf_exempt
def export_map_controller(request):
    try:
        req = request_to_object(request, ExportMapRequest)
        data = service.export_map(req)
    except Exception as e:
        return JsonResponse({'code': -1, 'error': str(e)})
    else:
        return JsonResponse({'code': 0, 'data': data})


@extend_schema(
    summary="查询网格时段数据",
)
@api_view(['POST'])
@csrf_exempt
def export_history_map_controller(request):
    try:
        data = service.export_history_map()
    except Exception as e:
        return JsonResponse({'code': -1, 'error': str(e)})
    else:
        return JsonResponse({'code': 0, 'data': data})


@extend_schema(
    summary="查询站点数据",
)
@api_view(['POST'])
@csrf_exempt
def export_station_controller(request):
    try:
        req = request_to_object(request, ExportStationRequest)
        data = service.export_station(req)
    except Exception as e:
        return JsonResponse({'code': -1, 'error': str(e)})
    else:
        return JsonResponse({'code': 0, 'data': data})


@extend_schema(
    summary="查询站点时段数据",
)
@api_view(['POST'])
@csrf_exempt
def export_history_station_controller(request):
    try:
        req = request_to_object(request, ExportHistoryStationRequest)
        data = service.get_station_by_project_and_station_name(req)
    except Exception as e:
        return JsonResponse({'code': -1, 'error': str(e)})
    else:
        return JsonResponse({'code': 0, 'data': data})


@extend_schema(
    summary="分页查询方案信息",
)
@api_view(['GET'])
@csrf_exempt
def project_pagination_controller(request, page, size):
    try:
        data = service.project_pagination(page, size)
    except Exception as e:
        return JsonResponse({'code': -1, 'error': str(e)})
    else:
        return JsonResponse({'code': 0, 'data': data})


@extend_schema(
    summary="分页查询实时预警信息",
)
@api_view(['GET'])
def forewarning_pagination_controller(request, page, size):
    """
    分页查询实时预警数据
    """
    if request.method == 'POST':
        return JsonResponse({'code': -1, 'error': 'Unsupported method'})
    try:
        data = service.forewarning_pagination(page, size)
    except Exception as e:
        return JsonResponse({'code': -1, 'error': str(e)})
    else:
        return JsonResponse({'code': 0, 'data': data})


@extend_schema(
    summary="查询站点代表数据",
)
@api_view(['POST'])
@csrf_exempt
def representation_station_controller(request):
    try:
        data = service.representation_station()
    except Exception as e:
        return JsonResponse({'code': -1, 'error': str(e)})
    else:
        return JsonResponse({'code': 0, 'data': data})


@extend_schema(
    summary="查询站点趋势数据",
)
@api_view(['POST'])
@csrf_exempt
def trend_station_controller(request, name):
    try:
        data = service.trend_station(name)
    except Exception as e:
        return JsonResponse({'code': -1, 'error': str(e)})
    else:
        return JsonResponse({'code': 0, 'data': data})


@extend_schema(
    summary="查询模型输入数据",
)
@api_view(['POST'])
@csrf_exempt
def latest_water_information_controller(request):
    try:
        data = service.latest_water_information()
    except Exception as e:
        return JsonResponse({'code': -1, 'error': str(e)})
    else:
        return JsonResponse({'code': 0, 'data': data})

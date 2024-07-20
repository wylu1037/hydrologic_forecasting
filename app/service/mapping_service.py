import json

import geopandas as gpd
import netCDF4 as nc
import numpy as np
from shapely import MultiPoint
from shapely.geometry import Polygon

from app.models import Project, ForecastGridData, WaterInformation
from app.repository.mapping_repository import MappingRepository
from manage import project_root_dir

WATER_DEPTH = 'wd'


def sort_vertices(lon, lat):
    """
    排序四角网格的顶点

    Args:
        lon(ndarray): 经度数组
        lat(ndarray): 纬度数组

    Returns:
        ndarray: [3 0 1 2]

    Example:
        sort_vertices([22.52566799 22.52892391 22.52876978 22.52475916], [113.86085031 113.86083196 113.85659267 113.8577512 ])
    """
    # 计算质心
    centroid = MultiPoint(list(zip(lon, lat))).centroid
    cx, cy = centroid.x, centroid.y

    # 计算每个顶点相对于质心的角度
    angles = np.arctan2(lat - cy, lon - cx)

    # 根据角度排序顶点
    sort_order = np.argsort(angles)

    # 返回排序后的顶点索引
    return sort_order


class MappingService:
    def __init__(self):
        self.repository = MappingRepository()

    @staticmethod
    def create_project(req):
        project = Project(name=req.name, description=req.description, time_index=req.time_index)
        project.save()
        return project.id

    @staticmethod
    def convert_nc_to_shp(req):
        root_dir = project_root_dir()
        nc_file = f'{root_dir}/storage/Mangkhut_4_map.nc'
        shp_file = f'{root_dir}/storage/water_depth_time{req.time_index}.shp'
        json_file_path = f'{root_dir}/storage/water_depth_time{req.time_index}.json'

        dataset = nc.Dataset(nc_file)

        # 获取经纬度和数据
        lon = dataset.variables['mesh2d_node_x'][:]
        lat = dataset.variables['mesh2d_node_y'][:]
        face_nodes = dataset.variables['mesh2d_face_nodes'][:]
        water_depth = dataset.variables['mesh2d_waterdepth'][:]  # 169, 61309
        water_depth = water_depth[req.time_index, :]  # 取第15个时间的水深数据，61309个网格

        # 判断是三角网格还是四角网格，并生成相应的几何图形
        geometries = []
        water_depth_arr = []
        json_arr = []
        project = Project.objects.get(pk=req.project_id)
        for i, face_node in enumerate(face_nodes):
            # 筛掉不满足水深条件的网格
            if water_depth[i] <= req.min_water_depth:
                continue

            node = face_node.compressed()
            if len(node) == 3:
                poly = Polygon([
                    (lon[node[0] - 1], lat[node[0] - 1]), (lon[node[1] - 1], lat[node[1] - 1]),
                    (lon[node[2] - 1], lat[node[2] - 1])
                ])

                data = {
                    'latLon': [
                        [lat[node[0] - 1], lon[node[0] - 1]],
                        [lat[node[1] - 1], lon[node[1] - 1]],
                        [lat[node[2] - 1], lon[node[2] - 1]],
                    ],
                    'depth': water_depth[i],
                }
                json_arr.append(data)

                ForecastGridData(
                    project=project,
                    longitude=[lon[node[0] - 1], lon[node[1] - 1], lon[node[2] - 1]],
                    latitude=[lat[node[0] - 1], lat[node[1] - 1], lat[node[2] - 1]],
                    water_depth=water_depth[i],
                ).save()
            elif len(node) == 4:
                sorted_nodes = sort_vertices(
                    np.array([lon[node[0] - 1], lon[node[1] - 1], lon[node[2] - 1], lon[node[3] - 1]]),
                    np.array([lat[node[0] - 1], lat[node[1] - 1], lat[node[2] - 1], lat[node[3] - 1]])
                )
                poly = Polygon([
                    (lon[node[sorted_nodes[0]] - 1], lat[node[sorted_nodes[0]] - 1]),
                    (lon[node[sorted_nodes[1]] - 1], lat[node[sorted_nodes[1]] - 1]),
                    (lon[node[sorted_nodes[2]] - 1], lat[node[sorted_nodes[2]] - 1]),
                    (lon[node[sorted_nodes[3]] - 1], lat[node[sorted_nodes[3]] - 1])
                ])

                data = {
                    'latLon': [
                        [lat[node[sorted_nodes[0]] - 1], lon[node[sorted_nodes[0]] - 1]],
                        [lat[node[sorted_nodes[1]] - 1], lon[node[sorted_nodes[1]] - 1]],
                        [lat[node[sorted_nodes[2]] - 1], lon[node[sorted_nodes[2]] - 1]],
                        [lat[node[sorted_nodes[3]] - 1], lon[node[sorted_nodes[3]] - 1]]
                    ],
                    'depth': water_depth[i],
                }
                json_arr.append(data)

                ForecastGridData(
                    project=project,
                    longitude=[lon[node[sorted_nodes[0]] - 1], lon[node[sorted_nodes[1]] - 1],
                               lon[node[sorted_nodes[2]] - 1], lon[node[sorted_nodes[3]] - 1]],
                    latitude=[lat[node[sorted_nodes[0]] - 1], lat[node[sorted_nodes[1]] - 1],
                              lat[node[sorted_nodes[2]] - 1], lat[node[sorted_nodes[3]] - 1]],
                    water_depth=water_depth[i],
                ).save()
            else:
                continue

            geometries.append(poly)
            water_depth_arr.append(water_depth[i])

        # 创建 GeoDataFrame
        gdf = gpd.GeoDataFrame({'geometry': geometries, WATER_DEPTH: water_depth_arr}, crs="EPSG:4326")

        # 保存为 .shp 文件
        gdf.to_file(shp_file)
        with open(file=json_file_path, mode="w") as json_file:
            json.dump(json_arr, json_file)

    @staticmethod
    def import_water_information(req):
        information = WaterInformation(
            station=req.station,
            datetime=req.datetime,
            upstream_water_level=req.upstream_water_level,
            downstream_water_level=req.downstream_water_level,
            flow=req.flow
        )
        information.save()
        return information.id

    @staticmethod
    def water_information_list(req):
        return WaterInformation.objects.filter(
            station=req.station, datetime__gte=req.start_datetime, datetime__lte=req.end_datetime).values(
            'upstream_water_level', 'downstream_water_level', 'flow')

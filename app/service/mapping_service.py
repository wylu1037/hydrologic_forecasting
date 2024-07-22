import json

import netCDF4 as nc
import numpy as np
from shapely import MultiPoint

from app.models import Project, MapData, StationData
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
    def handle_map(req):
        root_dir = project_root_dir()
        nc_file = f'{root_dir}/storage/output/FlowFM_map.nc'
        risk_nc_file = f'{root_dir}/storage/output/FlowFM_clm.nc'

        # 获取经纬度和数据
        dataset = nc.Dataset(nc_file)
        risk_ds = nc.Dataset(risk_nc_file)
        lon = dataset.variables['mesh2d_node_x'][:]
        lat = dataset.variables['mesh2d_node_y'][:]
        face_nodes = dataset.variables['mesh2d_face_nodes'][:]
        water_depth_arr = dataset.variables['mesh2d_waterdepth'][:]  # 169, 61309
        risk_arr = risk_ds.variables['mesh2d_waterdepth'][:]
        times = dataset.variables['time'][:]

        # 判断是三角网格还是四角网格，并生成相应的几何图形
        project = Project.objects.get(pk=req.project_id)
        for idx, time in enumerate(times):
            json_arr = []
            water_depth = water_depth_arr[idx, :]
            risk = risk_arr[idx, :]
            json_file_path = f'{root_dir}/storage/danyang_water_depth_time{idx}.json'
            for i, face_node in enumerate(face_nodes):
                # 筛掉不满足水深条件的网格
                if water_depth[i] <= req.min_water_depth:
                    continue

                node = face_node.compressed()
                if len(node) == 3:
                    data = {
                        'latLon': [
                            [lat[node[0] - 1], lon[node[0] - 1]],
                            [lat[node[1] - 1], lon[node[1] - 1]],
                            [lat[node[2] - 1], lon[node[2] - 1]],
                        ],
                        'depth': water_depth[i],
                        'risk': int(risk[i])
                    }
                    json_arr.append(data)

                    count = MapData.objects.filter(
                        project=project,
                        longitude=[lon[node[0] - 1], lon[node[1] - 1], lon[node[2] - 1]],
                        latitude=[lat[node[0] - 1], lat[node[1] - 1], lat[node[2] - 1]],
                        water_depth=water_depth[i],
                        risk=risk[i],
                        timestamp=int(time)
                    ).count()
                    if count == 0:
                        MapData(
                            project=project,
                            longitude=[lon[node[0] - 1], lon[node[1] - 1], lon[node[2] - 1]],
                            latitude=[lat[node[0] - 1], lat[node[1] - 1], lat[node[2] - 1]],
                            water_depth=water_depth[i],
                            risk=risk[i],
                            timestamp=int(time)
                        ).save()

                elif len(node) == 4:
                    sorted_nodes = sort_vertices(
                        np.array([lon[node[0] - 1], lon[node[1] - 1], lon[node[2] - 1], lon[node[3] - 1]]),
                        np.array([lat[node[0] - 1], lat[node[1] - 1], lat[node[2] - 1], lat[node[3] - 1]])
                    )

                    data = {
                        'latLon': [
                            [lat[node[sorted_nodes[0]] - 1], lon[node[sorted_nodes[0]] - 1]],
                            [lat[node[sorted_nodes[1]] - 1], lon[node[sorted_nodes[1]] - 1]],
                            [lat[node[sorted_nodes[2]] - 1], lon[node[sorted_nodes[2]] - 1]],
                            [lat[node[sorted_nodes[3]] - 1], lon[node[sorted_nodes[3]] - 1]]
                        ],
                        'depth': water_depth[i],
                        'risk': int(risk[i])
                    }
                    json_arr.append(data)

                    count = MapData.objects.filter(
                        project=project,
                        longitude=[lon[node[sorted_nodes[0]] - 1], lon[node[sorted_nodes[1]] - 1],
                                   lon[node[sorted_nodes[2]] - 1], lon[node[sorted_nodes[3]] - 1]],
                        latitude=[lat[node[sorted_nodes[0]] - 1], lat[node[sorted_nodes[1]] - 1],
                                  lat[node[sorted_nodes[2]] - 1], lat[node[sorted_nodes[3]] - 1]],
                        water_depth=water_depth[i],
                        risk=risk[i],
                        timestamp=int(time)
                    ).count()
                    if count == 0:
                        MapData(
                            project=project,
                            longitude=[lon[node[sorted_nodes[0]] - 1], lon[node[sorted_nodes[1]] - 1],
                                       lon[node[sorted_nodes[2]] - 1], lon[node[sorted_nodes[3]] - 1]],
                            latitude=[lat[node[sorted_nodes[0]] - 1], lat[node[sorted_nodes[1]] - 1],
                                      lat[node[sorted_nodes[2]] - 1], lat[node[sorted_nodes[3]] - 1]],
                            water_depth=water_depth[i],
                            risk=risk[i],
                            timestamp=int(time)
                        ).save()
                else:
                    continue

            with open(file=json_file_path, mode="w") as json_file:
                json.dump(json_arr, json_file)

    @staticmethod
    def handle_station():
        root_dir = project_root_dir()
        nc_file = f'{root_dir}/storage/output/FlowFM_his.nc'
        dataset = nc.Dataset(nc_file)

        lon = dataset.variables['station_x_coordinate'][:]
        lat = dataset.variables['station_y_coordinate'][:]
        times = dataset.variables['time'][:]
        water_depth = dataset.variables['waterdepth'][:]
        water_level = dataset.variables['waterlevel'][:]
        velocity_magnitude = dataset.variables['velocity_magnitude'][:]

        project = Project.objects.get(pk=1)

        json_arr = []
        for i, time in enumerate(times):
            json_file_path = f'{root_dir}/storage/danyang_station_time{i}.json'
            for j in range(lon.size):
                StationData(
                    project=project,
                    longitude=lon[j],
                    latitude=lat[j],
                    water_depth=water_depth[i, j],
                    water_level=water_level[i, j],
                    velocity_magnitude=velocity_magnitude[i, j],
                    timestamp=int(time),
                ).save()

                data = {
                    'lon': lon[j],
                    'lat': lat[j],
                    'time': time,
                    'waterDepth': water_depth[i, j],
                    'waterLevel': water_level[i, j],
                    'velocityMagnitude': velocity_magnitude[i, j],
                }
                json_arr.append(data)
            with open(file=json_file_path, mode="w") as json_file:
                json.dump(json_arr, json_file)

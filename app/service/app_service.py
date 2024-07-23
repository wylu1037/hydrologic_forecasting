import json
import os
import subprocess

import netCDF4 as nc
import numpy as np
from shapely import MultiPoint

from app.convert import timestamp_to_datetime, datetime_to_timestamp
from app.models import Project
from app.repository.app_repository import AppRepository
from manage import project_root_dir


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


class AppService:
    # private var
    _app_repository_instance = None

    def __init__(self):
        if not AppService._app_repository_instance:
            self._app_repository_instance = AppRepository()
        self.repository = self._app_repository_instance

    @staticmethod
    def run(req):
        """
        运行模型脚本
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        bat_path = os.path.join(project_root_dir(), 'script.sh')
        result = subprocess.run([bat_path] + req.args, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr)
        else:
            return result.stdout

    @staticmethod
    def create_project(req):
        """
        创建项目
        """
        project = Project(name=req.name, description=req.description, time_index=req.time_index)
        project.save()
        return project.id

    def handle_map(self, req):
        """
        处理网格数据
        """
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

                    self.repository.upsert_map(
                        project,
                        [lon[node[0] - 1], lon[node[1] - 1], lon[node[2] - 1]],
                        [lat[node[0] - 1], lat[node[1] - 1], lat[node[2] - 1]],
                        water_depth[i],
                        risk[i],
                        time
                    )
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

                    self.repository.upsert_map(
                        project,
                        [lon[node[sorted_nodes[0]] - 1], lon[node[sorted_nodes[1]] - 1], lon[node[sorted_nodes[2]] - 1],
                         lon[node[sorted_nodes[3]] - 1]],
                        [lat[node[sorted_nodes[0]] - 1], lat[node[sorted_nodes[1]] - 1], lat[node[sorted_nodes[2]] - 1],
                         lat[node[sorted_nodes[3]] - 1]],
                        water_depth[i],
                        risk[i],
                        time
                    )
                else:
                    continue

            with open(file=json_file_path, mode="w") as json_file:
                json.dump(json_arr, json_file)

    def handle_station(self):
        """
        处理站点数据
        """
        root_dir = project_root_dir()
        nc_file = f'{root_dir}/storage/output/FlowFM_his.nc'
        dataset = nc.Dataset(nc_file)

        lon = dataset.variables['station_x_coordinate'][:]
        lat = dataset.variables['station_y_coordinate'][:]
        station_names = dataset.variables['station_name'][:]
        times = dataset.variables['time'][:]
        water_depth = dataset.variables['waterdepth'][:]
        water_level = dataset.variables['waterlevel'][:]
        velocity_magnitude = dataset.variables['velocity_magnitude'][:]

        project = Project.objects.get(pk=1)

        # json_arr = []
        for i, time in enumerate(times):
            # json_file_path = f'{root_dir}/storage/danyang_station_time{i}.json'
            for j in range(lon.size):
                station_name = ''.join([name.strip() for name in station_names[j].compressed().astype(str) if name])
                self.repository.upsert_station(
                    project, station_name, lon[j], lat[j], water_depth[i, j], water_level[i, j],
                    velocity_magnitude[i, j], time)

                # data = {
                #     'lon': lon[j],
                #     'lat': lat[j],
                #     'time': time,
                #     'waterDepth': water_depth[i, j],
                #     'waterLevel': water_level[i, j],
                #     'velocityMagnitude': velocity_magnitude[i, j],
                # }
                # json_arr.append(data)
            # with open(file=json_file_path, mode="w") as json_file:
            #     json.dump(json_arr, json_file)

    def export_map(self, req):
        """
        导出网格数据
        """
        if req.project_id is None:
            req.project_id = self.repository.get_latest_project().id
        project = Project.objects.get(pk=req.project_id)
        start_time = datetime_to_timestamp(req.start_time)
        end_time = datetime_to_timestamp(req.end_time)
        data = self.repository.get_map_list(project, start_time, end_time)
        json_array = []
        for elem in data:
            json_data = {
                'id': elem[0],
                'coordinates': [[y, x] for x, y in zip(elem[1], elem[2])],
                'waterDepth': elem[3],
                'risk': elem[4],
                'time': timestamp_to_datetime(elem[5])
            }
            json_array.append(json_data)
        return json_array

    def export_station(self, req):
        """
        导出站点数据
        """
        if req.project_id is None:
            req.project_id = self.repository.get_latest_project().id
        project = Project.objects.get(pk=req.project_id)
        start_time = datetime_to_timestamp(req.start_time)
        end_time = datetime_to_timestamp(req.end_time)
        data = self.repository.get_station_list(project, start_time, end_time)
        json_array = []
        for elem in data:
            json_data = {
                'id': elem[0],
                'lon': elem[1],
                'lat': elem[2],
                'waterDepth': elem[3],
                'waterLevel': elem[4],
                'velocityMagnitude': elem[5],
                'stationName': elem[6],
                'time': timestamp_to_datetime(elem[7]),
            }
            json_array.append(json_data)
        return json_array

    def project_pagination(self, page, size):
        return self.repository.project_pagination(page, size)

    def representation_station(self):
        data = self.repository.representation_station()

        json_arr = []
        for elem in data:
            json_data = {
                'id': elem['id'],
                'stationName': elem['station_name'],
                'waterDepth': elem['water_depth'],
                'velocityMagnitude': elem['velocity_magnitude'],
                'time': timestamp_to_datetime(elem['timestamp'])
            }
            json_arr.append(json_data)
        return json_arr

    def trend_station(self, name):
        data = self.repository.trend_station(name)

        json_arr = []
        for elem in data:
            json_data = {
                'id': elem['id'],
                'stationName': elem['station_name'],
                'waterDepth': elem['water_depth'],
                'waterLevel': elem['water_level'],
                'velocityMagnitude': elem['velocity_magnitude'],
                'time': timestamp_to_datetime(elem['timestamp']),
            }
            json_arr.append(json_data)
        return json_arr

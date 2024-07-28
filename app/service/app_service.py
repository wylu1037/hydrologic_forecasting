import os
import subprocess

import netCDF4 as nc
import numpy as np
from shapely import MultiPoint
import pandas as pd

from app.models import Project
from app.repository.app_repository import AppRepository
from app.request import HandleMapRequest, HandleStationRequest
from app.tools import search_file, convert_map_data_to_json, convert_station_data_to_json
from app.tools import timestamp_to_datetime
from hydrologic_forecasting.settings import config


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

    def run_project(self, req):
        """
        创建项目，并运行模型
        """
        # write input data
        # WaterLevel.bc Discharge.bc
        if req.upstream_water_level is None or req.downstream_water_level is None:
            res = self.latest_water_information(req.start_time)
            req.upstream_water_level = res['upstreamWaterLevel']
            req.downstream_water_level = res['downstreamWaterLevel']
        #write_upstream_water_level(req.upstream_water_level)
        #write_downstream_water_level(req.downstream_water_level)

        datetimes = []
        for v in req.upstream_water_level:
            datetimes.append(v['datetime'])

        self.handle_map(HandleMapRequest(project_id=1), datetimes)

        # execute bat
        bat_path = config['model']['script']['bat_path']
        result = subprocess.run([bat_path], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr)
        else:
            # 执行成功
            project_id = self.repository.insert_project(req)
            self.handle_map(HandleMapRequest(project_id=project_id))
            self.handle_station(HandleStationRequest(project_id=project_id))
            return result.stdout

    def project_list(self):
        data = self.repository.project_list()
        json_arr = []
        for item in data:
            json_arr.append(
                {
                    'id': item[0],
                    'name': item[1],
                    'description': item[2],
                    'forecastPeriod': item[3],
                }
            )
        return json_arr

    def update_project(self, req):
        self.repository.update_project(req)

    def delete_project(self, project_id):
        self.repository.delete_project(project_id)

    def handle_map(self, req, date_times=None):
        """
        处理网格数据
        """
        output_dir = config['model']['script']['output']
        nc_file = search_file(output_dir, '_map.nc')
        risk_nc_file = search_file(output_dir, 'Modified_FlowFM_clm.nc')

        # 获取经纬度和数据
        dataset = nc.Dataset(nc_file)
        risk_ds = nc.Dataset(risk_nc_file)
        lon = dataset.variables['mesh2d_node_x'][:]
        lat = dataset.variables['mesh2d_node_y'][:]
        face_nodes = dataset.variables['mesh2d_face_nodes'][:]
        water_depth_arr = dataset.variables['mesh2d_waterdepth'][:]  # 169, 61309
        risk_arr = risk_ds.variables['mesh2d_waterdepth'][:]
        times = dataset.variables['time'][:]
        if date_times is not None:
            times = date_times

        # 判断是三角网格还是四角网格，并生成相应的几何图形
        project = self.repository.get_project_by_id(req.project_id)
        # idx 0-23  0   1
        for idx, time in enumerate(times):
            if project.type == 0 and idx < 23:
                continue
            if project.type == 1 and idx < 24:
                continue

            water_depth = water_depth_arr[idx, :]
            risk = risk_arr[idx, :]
            for i, face_node in enumerate(face_nodes):
                # 筛掉不满足水深条件的网格
                if water_depth[i] <= req.min_water_depth:
                    continue

                node = face_node.compressed()
                if len(node) == 3:
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

    def handle_station(self, req, date_times=None):
        """
        处理站点数据
        """
        output_dir = config['model']['script']['output']
        nc_file = search_file(output_dir, '_his.nc')
        dataset = nc.Dataset(nc_file)

        lon = dataset.variables['station_x_coordinate'][:]
        lat = dataset.variables['station_y_coordinate'][:]
        station_names = dataset.variables['station_name'][:]
        times = dataset.variables['time'][:]
        if date_times is not None:
            times = date_times
        water_depth = dataset.variables['waterdepth'][:]
        water_level = dataset.variables['waterlevel'][:]
        velocity_magnitude = dataset.variables['velocity_magnitude'][:]

        project = self.repository.get_project_by_id(req.project_id)
        for i, time in enumerate(times):
            # 计算好的模型只需要最后1个小时
            if project.type == 0 and i < 23:
                continue
            # 实时计算的模型需要取[24:47]
            if project.type == 1 and i < 24:
                continue
            for j in range(lon.size):
                station_name = ''.join([name.strip() for name in station_names[j].compressed().astype(str) if name])
                self.repository.upsert_station(
                    project, station_name, lon[j], lat[j], water_depth[i, j], water_level[i, j],
                    velocity_magnitude[i, j], time)

    def export_map(self, req):
        """
        导出网格数据
        """
        if req.project_id is None:
            req.project_id = self.repository.get_latest_project().id
        project = self.repository.get_project_by_id(req.project_id)

        times = self.repository.get_map_times(project)
        data = self.repository.get_map_by_project_and_timestamp(project, times[0]['timestamp'])
        return convert_map_data_to_json(data)

    def export_history_map(self, req):
        if req.project_id is None:
            req.project_id = self.repository.get_latest_project().id
        project = Project.objects.get(pk=req.project_id)
        return self.repository.get_history_map(project)

    def export_station(self, req):
        """
        导出站点数据
        """
        if req.project_id is None:
            req.project_id = self.repository.get_latest_project().id
        project = Project.objects.get(pk=req.project_id)

        times = self.repository.get_station_times(project)
        data = self.repository.get_station_by_project_and_timestamp(project, times[0]['timestamp'])
        return convert_station_data_to_json(data)

    def project_pagination(self, page, size):
        return self.repository.project_pagination(page, size)

    def forewarning_pagination(self, page, size):
        project = self.repository.get_latest_project()
        data = self.repository.forewarning_pagination(project, page, size)
        json_array = []
        for elem in data['items']:
            json_data = {
                'id': elem[0],
                'coordinates': [[y, x] for x, y in zip(elem[1], elem[2])],
                'waterDepth': elem[3],
                'riskLevel': elem[4],
                'warningLevel': WARNING_RISK_DICT[elem[4]],
                'time': timestamp_to_datetime(elem[5]),
                'createdAt': elem[6].strftime('%Y-%m-%d %H:%M:%S'),
            }
            json_array.append(json_data)

        return {
            'items': json_array,
            'page': data['page'],
            'size': data['size'],
            'total': data['total'],
        }

    def representation_station(self, req):
        if req.project_id is None:
            req.project_id = self.repository.get_latest_project().id
        data = self.repository.representation_station(req.project_id)

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

    def latest_water_information(self, start_time=None):
        rainfall = self.repository.get_latest_rainfall(start_time)
        upstream_water_level = self.repository.get_latest_upstream_water_level(start_time)
        downstream_water_level = self.repository.get_latest_downstream_water_level(start_time)

        return {
            'rainfall': rainfall,
            'upstreamWaterLevel': upstream_water_level,
            'downstreamWaterLevel': downstream_water_level
        }

    def get_station_by_project_and_station_name(self, req):
        if req.project_id is None:
            req.project_id = self.repository.get_latest_project().id
        project = Project.objects.get(pk=req.project_id)

        data = self.repository.get_station_by_project_and_station_name(project, req.name)
        return convert_station_data_to_json(data)

    def handle_rainfall_series(self):
        csv_path = config['model']['script']['rainfall_path']
        data = pd.read_csv(csv_path, encoding='latin1')
        # for i, column in enumerate(np.transpose(data.values)):
        #     if i == 0:
        #         continue
        #     print(column)
        project_arr = [2, 3, 4, 5, 6]
        for i, column in enumerate(data.iloc[:, 1:].values.T):  # .values.T 将 DataFrame 转置，便于逐列遍历
            project = self.repository.get_project_by_id(project_arr[i])
            for elem in column:
                self.repository.upsert_rainfall_series(project, elem)

    def get_rainfall_series(self, project_id):
        project = self.repository.get_project_by_id(project_id)
        return self.repository.get_rainfall_series(project)


WARNING_RISK_DICT = {
    1: "较低风险",
    2: "中等风险",
    3: "较高风险",
    4: "高风险",
}


def write_downstream_water_level(downstream_water_level):
    data_str = ""
    times = [
        649296000, 649299600, 649303200, 649306800, 649310400, 649314000, 649317600, 649321200, 649324800,
        649328400, 649332000, 649335600, 649339200, 649342800, 649346400, 649350000, 649353600, 649357200,
        649360800, 649364400, 649368000, 649371600, 649375200, 649378800, 649382400, 649386000, 649389600,
        649393200, 649396800, 649400400, 649404000, 649407600, 649411200, 649414800, 649418400, 649422000,
        649425600, 649429200, 649432800, 649436400, 649440000, 649443600, 649447200, 649450800, 649454400,
        649458000, 649461600, 649465200
    ]
    for i, elem in enumerate(downstream_water_level):
        data_str += f"{times[i]}  {elem['data']}\n"

    content = f"""[forcing]
Name                            = WL_0001
Function                        = timeseries
Time-interpolation              = linear
Quantity                        = time
Unit                            = seconds since 2001-01-01 00:00:00
Quantity                        = waterlevelbnd
Unit                            = m
{data_str}
[forcing]
Name                            = WL_0002
Function                        = timeseries
Time-interpolation              = linear
Quantity                        = time
Unit                            = seconds since 2001-01-01 00:00:00
Quantity                        = waterlevelbnd
Unit                            = m
{data_str}"""

    input_dir = config['model']['script']['input']
    path = os.path.join(input_dir, "WaterLevel.bc")
    if os.path.exists(path):
        os.remove(path)

    with open(path, "w") as file:
        file.write(content)


def write_upstream_water_level(upstream_water_level):
    data_str = ""
    times = [
        649296000, 649299600, 649303200, 649306800, 649310400, 649314000, 649317600, 649321200, 649324800,
        649328400, 649332000, 649335600, 649339200, 649342800, 649346400, 649350000, 649353600, 649357200,
        649360800, 649364400, 649368000, 649371600, 649375200, 649378800, 649382400, 649386000, 649389600,
        649393200, 649396800, 649400400, 649404000, 649407600, 649411200, 649414800, 649418400, 649422000,
        649425600, 649429200, 649432800, 649436400, 649440000, 649443600, 649447200, 649450800, 649454400,
        649458000, 649461600, 649465200,
    ]
    for i, elem in enumerate(upstream_water_level):
        data_str += f"{times[i]}  {elem['data']}\n"

    content = f"""[forcing]
Name                            = Boundary01_0001
Function                        = timeseries
Time-interpolation              = linear
Quantity                        = time
Unit                            = seconds since 2001-01-01 00:00:00
Quantity                        = dischargebnd
Unit                            = m3/s
{data_str}
[forcing]
Name                            = Boundary01_0002
Function                        = timeseries
Time-interpolation              = linear
Quantity                        = time
Unit                            = seconds since 2001-01-01 00:00:00
Quantity                        = dischargebnd
Unit                            = m3/s
{data_str}"""

    input_dir = config['model']['script']['input']
    path = os.path.join(input_dir, "Discharge.bc")
    if os.path.exists(path):
        os.remove(path)

    with open(path, "w") as file:
        file.write(content)

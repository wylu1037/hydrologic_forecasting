from django.core.paginator import Paginator
from django.db import connection

from app.models import StationData, MapData, Project, UpstreamWaterLevel, DownstreamWaterLevel, Rainfall, RainfallSeries
from app.tools import timestamp_to_datetime, convert_map_data_to_json, datetime_to_timestamp


class AppRepository:
    @staticmethod
    def upsert_map(project, lon, lat, water_depth, risk, timestamp):
        """
        保存网格数据

        Args:
            project
            lon(list)
            lat(list)
            water_depth(float)
            risk(int)
            timestamp(float or str)

        Returns
            int
        """
        if timestamp is float:
            converted_timestamp = int(timestamp)
        else:
            converted_timestamp = datetime_to_timestamp(timestamp)
        count = MapData.objects.filter(
            project=project,
            longitude=lon,
            latitude=lat,
            water_depth=water_depth,
            risk=risk,
            timestamp=converted_timestamp
        ).count()
        if count > 0:
            return None

        data = MapData(
            project=project,
            longitude=lon,
            latitude=lat,
            water_depth=water_depth,
            risk=risk,
            timestamp=converted_timestamp,
        )
        data.save()
        return data.id

    @staticmethod
    def upsert_station(project, station_name, lon, lat, water_depth, water_level, velocity_magnitude, timestamp):
        if timestamp is float:
            converted_timestamp = int(timestamp)
        else:
            converted_timestamp = datetime_to_timestamp(timestamp)
        count = StationData.objects.filter(
            project=project, station_name=station_name, longitude=lon, latitude=lat, water_depth=water_depth,
            water_level=water_level, velocity_magnitude=velocity_magnitude,
            timestamp=converted_timestamp).count()
        if count > 0:
            return None

        data = StationData(
            project=project,
            station_name=station_name,
            longitude=lon,
            latitude=lat,
            water_depth=water_depth,
            water_level=water_level,
            velocity_magnitude=velocity_magnitude,
            timestamp=converted_timestamp,
        )
        data.save()

        return data.pk

    @staticmethod
    def get_map_by_project_and_timestamp(project, timestamp):
        data = (MapData.objects
                .filter(project=project, timestamp=timestamp)
                .values_list('id', 'longitude', 'latitude', 'water_depth', 'risk', 'timestamp')
                )
        return list(data)

    @staticmethod
    def get_latest_project():
        return Project.objects.order_by('-id').first()

    @staticmethod
    def project_pagination(page, size):
        projects = Project.objects.all().order_by('-id')
        paginator = Paginator(projects, size)
        items = paginator.get_page(page)
        data = {
            'items': list(items.object_list.values_list('id', 'name', 'description', 'created_at', 'forecast_period',
                                                        'type')),
            'page': items.number,
            'size': size,
            'total': paginator.count
        }
        return data

    @staticmethod
    def forewarning_pagination(project, page, size):
        rows = MapData.objects.filter(project=project).order_by('-id')
        paginator = Paginator(rows, size)
        items = paginator.get_page(page)

        data = {
            'items': list(
                items.object_list.values_list(
                    'id', 'longitude', 'latitude', 'water_depth', 'risk', 'timestamp', 'created_at')),
            'page': items.number,
            'size': size,
            'total': paginator.count
        }
        return data

    @staticmethod
    def representation_station(project_id):
        query = """
        select id, station_name, max(water_depth) as water_depth, max(velocity_magnitude) as velocity_magnitude, timestamp
        from (select *
              from app_stationdata
              where project_id = %s
              order by id desc
              limit 480)
        group by timestamp;
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [project_id])
            columns = [col[0] for col in cursor.description]
            data = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
        return data

    @staticmethod
    def trend_station(name):
        query = """
        select id, station_name, water_depth, water_level, velocity_magnitude, timestamp
        from (select *
              from app_stationdata
              order by id desc
              limit 480)
        where station_name = %s
        order by timestamp;
                """
        with connection.cursor() as cursor:
            cursor.execute(query, [name])
            columns = [col[0] for col in cursor.description]
            data = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
        return data

    @staticmethod
    def get_project_by_id(project_id):
        try:
            project = Project.objects.get(pk=project_id)
            return project
        except Project.DoesNotExist:
            raise ValueError(f'项目方案 {project_id} 不存在，请检查参数是否正确')

    @staticmethod
    def insert_project(req):
        project = Project(name=req.name, description=req.description, forecast_period=req.forecast_period,
                          start_time=req.start_time, type=req.type)
        project.save()
        return project.id

    @staticmethod
    def update_project(req):
        project = Project.objects.get(id=req.id)
        if req.name is not None:
            project.name = req.name
        if req.description is not None:
            project.description = req.description
        if req.forecast_period is not None:
            project.forecast_period = req.forecast_period
        project.save()

    @staticmethod
    def delete_project(project_id):
        project = Project.objects.get(id=project_id)
        project.delete()

    @staticmethod
    def upsert_upstream_water_level(station_name, datetime, data):
        count = UpstreamWaterLevel.objects.filter(
            station=station_name,
            datetime=datetime,
        ).count()
        if count > 0:
            return None

        model_data = UpstreamWaterLevel(
            station=station_name,
            datetime=datetime,
            data=data
        )
        model_data.save()
        return model_data.id

    @staticmethod
    def upsert_downstream_water_level(station_name, datetime, data):
        count = DownstreamWaterLevel.objects.filter(
            station=station_name,
            datetime=datetime,
        ).count()
        if count > 0:
            return None

        model_data = DownstreamWaterLevel(
            station=station_name,
            datetime=datetime,
            data=data
        )
        model_data.save()
        return model_data.id

    @staticmethod
    def get_latest_upstream_water_level(start_time=None):
        if start_time is None:
            result = UpstreamWaterLevel.objects.order_by('datetime')[:48].values_list('station', 'datetime', 'data')
            return convert_to_json(result)
        else:
            result = UpstreamWaterLevel.objects.filter(datetime__gte=start_time).order_by('datetime')[:48].values_list(
                'station', 'datetime', 'data')
            return convert_to_json(result)

    @staticmethod
    def get_latest_downstream_water_level(start_time=None):
        if start_time is None:
            result = DownstreamWaterLevel.objects.order_by('datetime')[:48].values_list('station', 'datetime', 'data')
            return convert_to_json(result)
        else:
            result = DownstreamWaterLevel.objects.filter(datetime__gte=start_time).order_by('datetime')[:48].values_list('station', 'datetime', 'data')
            return convert_to_json(result)

    @staticmethod
    def get_latest_rainfall(start_time=None):
        if start_time is None:
            result = Rainfall.objects.order_by('datetime')[:48].values_list('station', 'datetime', 'data')
            return convert_to_json(result)
        else:
            result = Rainfall.objects.filter(datetime__gte=start_time).order_by('datetime')[:48].values_list('station',
                                                                                                             'datetime',
                                                                                                             'data')
            return convert_to_json(result)

    @staticmethod
    def get_map_times(project):
        times = MapData.objects.filter(project=project).values('timestamp').distinct().order_by('-timestamp')
        return times

    @staticmethod
    def get_map_by_project_and_timestamp(project, timestamp):
        data = (
            MapData.objects.filter(project=project, timestamp=timestamp)
            .values_list('id', 'longitude', 'latitude', 'water_depth',
                         'risk', 'timestamp')
        )
        return list(data)

    @staticmethod
    def get_history_map(project):
        times = AppRepository.get_map_times(project)
        arr = []
        for time in times:
            data = AppRepository.get_map_by_project_and_timestamp(project, time['timestamp'])
            datetime = timestamp_to_datetime(time['timestamp'])
            arr.append({
                'time': datetime,
                'data': convert_map_data_to_json(data)
            })

        return arr

    @staticmethod
    def get_station_times(project):
        times = StationData.objects.filter(project=project).values('timestamp').distinct().order_by('-timestamp')
        return times

    @staticmethod
    def get_station_by_project_and_timestamp(project, timestamp):
        data = (
            StationData.objects.filter(project=project, timestamp=timestamp)
            .values_list('id',
                         'longitude',
                         'latitude',
                         'water_depth',
                         'water_level',
                         'velocity_magnitude',
                         'station_name',
                         'timestamp')
        )
        return list(data)

    @staticmethod
    def get_station_by_project_and_station_name(project, station_name):
        data = (
            StationData.objects.filter(project=project, station_name=station_name)
            .order_by('-timestamp')
            .values_list('id',
                         'longitude',
                         'latitude',
                         'water_depth',
                         'water_level',
                         'velocity_magnitude',
                         'station_name',
                         'timestamp')
        )
        return list(data)

    @staticmethod
    def project_list():
        data = (
            Project.objects.all()
            .values_list('id', 'name', 'description', 'forecast_period', 'type')
            .order_by('-id')
        )
        return list(data)

    @staticmethod
    def upsert_rainfall_series(project, rainfall):
        count = RainfallSeries.objects.filter(project=project, rainfall=rainfall).count()
        if count > 0:
            return None

        data = RainfallSeries(
            project=project,
            rainfall=rainfall
        )
        data.save()
        return data.id

    @staticmethod
    def get_rainfall_series(project):
        data = RainfallSeries.objects.filter(project=project).values_list('id', 'rainfall')
        json_arr = []
        for elem in list(data):
            json_arr.append({
                "id": elem[0],
                "rainfall": elem[1]
            })
        return json_arr


def convert_to_json(result):
    json_arr = []
    for station, datetime, data in result:
        json_arr.append({
            'station': station,
            'datetime': datetime.strftime('%Y-%m-%d %H:%M:%S'),
            'data': data
        })
    return json_arr

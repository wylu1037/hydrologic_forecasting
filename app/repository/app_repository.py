from app.models import StationData, MapData


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
            timestamp(float)

        Returns
            int
        """
        count = MapData.objects.filter(
            project=project,
            longitude=lon,
            latitude=lat,
            water_depth=water_depth,
            risk=risk,
            timestamp=int(timestamp)
        ).count()
        if count > 0:
            return None

        data = MapData(
            project=project,
            longitude=lon,
            latitude=lat,
            water_depth=water_depth,
            risk=risk,
            timestamp=int(timestamp),
        )
        data.save()
        return data.id

    @staticmethod
    def upsert_station(project, station_name, lon, lat, water_depth, water_level, velocity_magnitude, timestamp):
        count = StationData.objects.filter(
            project=project, station_name=station_name, longitude=lon, latitude=lat, water_depth=water_depth,
            water_level=water_level, velocity_magnitude=velocity_magnitude,
            timestamp=int(timestamp)).count()
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
            timestamp=int(timestamp),
        )
        data.save()

        return data.pk

    @staticmethod
    def get_map_list(project, start_time, end_time):
        data = (MapData.objects
                .filter(project=project, timestamp__gte=start_time, timestamp__lte=end_time)
                .values_list('id', 'longitude', 'latitude', 'water_depth', 'risk', 'timestamp')
                )
        return list(data)

    @staticmethod
    def get_station_list(project, start_time, end_time):
        data = (StationData.objects
                .filter(project=project, timestamp__gte=start_time, timestamp__lte=end_time)
                .values_list('id',
                             'longitude',
                             'latitude',
                             'water_depth',
                             'water_level',
                             'velocity_magnitude',
                             'station_name',
                             'timestamp'
                             )
                )
        return list(data)

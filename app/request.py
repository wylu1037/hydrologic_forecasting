class ModelForecastRequest:
    def __init__(self, scheme_name, date_time, step_size, schem_description, args):
        self.scheme_name = scheme_name
        self.date_time = date_time
        self.step_size = step_size
        self.schem_description = schem_description
        self.args = args


class ConvertNcRequest:
    def __init__(self, project_id, time_index=15, min_water_depth=0.01):
        self.project_id = project_id
        self.time_index = time_index
        self.min_water_depth = min_water_depth


class CreateProjectRequest:
    def __init__(self, name, description, time_index):
        self.name = name
        self.description = description
        self.time_index = time_index


class ImportWaterInformationRequest:
    def __init__(self, station, datetime, upstream_water_level, downstream_water_level, flow):
        self.station = station
        self.datetime = datetime
        self.upstream_water_level = upstream_water_level
        self.downstream_water_level = downstream_water_level
        self.flow = flow


class WaterInformationListRequest:
    def __init__(self, station, start_datetime, end_datetime):
        self.station = station
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime

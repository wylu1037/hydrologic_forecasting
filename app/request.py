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

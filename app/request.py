class ModelForecastRequest:
    def __init__(self, scheme_name, date_time, step_size, schem_description, args):
        self.scheme_name = scheme_name
        self.date_time = date_time
        self.step_size = step_size
        self.schem_description = schem_description
        self.args = args

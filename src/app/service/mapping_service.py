from src.app.repository.mapping_repository import MappingRepository

from src.tools.convert import Converter


class MappingService:
    def __init__(self):
        self.repository = MappingRepository()

    @staticmethod
    def convert_nc_to_shp():
        nc_file = '/Users/wenyanglu/Workspace/github/hydrologic_forecasting/storage/Mangkhut_4_map.nc'
        shp_file = '/Users/wenyanglu/Workspace/github/hydrologic_forecasting/storage/water_depth.shp'
        html_file = '/Users/wenyanglu/Workspace/github/hydrologic_forecasting/storage/water_depth.html'
        Converter.map_to_shp_and_html(nc_file, shp_file, html_file)

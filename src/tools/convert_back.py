import datetime

import geojson
import netCDF4 as nc
import numpy as np
import pandas as pd
import rasterio
import xarray as xr
from pyproj import Proj, transform
from rasterio.transform import from_origin, from_bounds


class Converter:
    @staticmethod
    def netcdf_to_geojson(netcdf_file, lon_variable, lat_variable, data_variables, geojson_name):
        """
        Returns: a GeoJSON file created from the data in a structured NetCDF file, with coordinates following an
        equidistant cylindrical projection (EPSG:4087) and properties storing specified data variables.

        Parameters:
        nc_file: String. Path and name of structured NetCDF file to convert.
        lon_variable: String. Name of coordinate variable used to represent the data on a horizontal basis in the NetCDF file (i.e. 'lon', 'x').
        lat_variable: String. Name of coordinate variable used to represent the data on a vertical basis in the NetCDF file (i.e. 'lat', 'y').
        data_variables: List[String]. List of data variables of interest from the NetCDF file. Will be retained as properties of the GeoJSON file.
        geojson_name: String. Path and name of desired GeoJSON file output.
        """
        # open dataset
        ds = xr.open_dataset(netcdf_file)

        # "reprojecting" by making new coordinate arrays following the equidistant cylindrical projection
        step_lon = 360 / ds[lon_variable].size
        step_lat = 180 / ds[lat_variable].size

        reproject_lon = np.arange(-180, 180, step_lon)
        reproject_lat = np.arange(-90, 90, step_lat)

        new_latitude_var = xr.DataArray(reproject_lat, dims="latitude")
        new_longitude_var = xr.DataArray(reproject_lon, dims="longitude")

        # update the dataset with new coordinate variables
        ds["latitude"] = new_latitude_var
        ds["longitude"] = new_longitude_var

        # identify key variables
        latitude = ds["latitude"]
        latitude_range = len(latitude)
        longitude = ds["longitude"]
        longitude_range = len(longitude)

        # print("Dataset variables:", ds.keys())

        # prepare GeoJSON
        geojson_features = []

        # loop over all coordinate pairs
        for i in range(latitude_range):
            for j in range(longitude_range):
                lat = float(latitude[i])
                lon = float(longitude[j])
                properties = {}

                # add each data variable to the properties
                for data_variable in data_variables:
                    data_var = ds[data_variable]
                    if data_var.ndim == 2:  # .shape 2D
                        data_value = float(data_var[i, j])
                    else:
                        if data_variable == "time":
                            timestamp = int(data_var[i]) / 10 ** 9
                            data_value = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                        else:
                            data_value = float(data_var[i])

                    properties[data_variable] = data_value

                # Create a GeoJSON feature for each point
                point = geojson.Point((lon, lat))
                feature = geojson.Feature(geometry=point, properties=properties)
                geojson_features.append(feature)

        # write GeoJSON to File
        with open(geojson_name, "w") as f:
            geojson.dump(geojson.FeatureCollection(geojson_features), f)

    # Example usage Converter.netcdf_to_geojson("../../storage/Mangkhut_4_his.nc", "station_x_coordinate",
    # "station_y_coordinate", ["waterdepth", "waterlevel", "velocity_magnitude", "time"], "../../storage/his.geojson")

    @staticmethod
    def netcdf_to_tif(nc_file, variable_name, lon_variable, lat_variable, tif_file):
        """
        Converts a NetCDF file to a GeoTIFF file.

        Parameters:
        nc_file: str - Path to the NetCDF file.
        variable_name: str - Name of the variable to be converted.
        tif_file: str - Path to the output GeoTIFF file.
        """
        # Open the NetCDF file
        ds = xr.open_dataset(nc_file)

        # Extract the variable of interest
        data = ds[variable_name]

        # Get the spatial resolution and origin
        lon = ds[lon_variable]
        lat = ds[lat_variable]

        # Ensure the data is 2D
        if len(data.shape) != 2:
            raise ValueError("The variable is not 2D.")

        # 定义地理坐标系
        geographic = Proj(init='epsg:4326')

        # 定义投影坐标系（例如，WGS1984 UTM Zone 33N）
        projected = Proj(init='epsg:32633')

        # 转换经纬度坐标到投影坐标
        lon2d, lat2d = np.meshgrid(lon, lat)
        x, y = transform(geographic, projected, lon2d, lat2d)

        # 获取数据范围和分辨率
        min_x, min_y, max_x, max_y = x.min(), y.min(), x.max(), y.max()
        resolution_x = (max_x - min_x) / data.shape[1]
        resolution_y = (max_y - min_y) / data.shape[0]

        # 创建投影变换
        my_transform = from_bounds(min_x, min_y, max_x, max_y, data.shape[1], data.shape[0])

        # Write to GeoTIFF
        with rasterio.open(
                fp=tif_file,
                mode='w',
                driver='GTiff',
                height=data.shape[0],
                width=data.shape[1],
                count=1,
                dtype=data.dtype,
                crs=projected.crs,  # Assuming WGS84 latitude/longitude
                transform=my_transform,
        ) as dst:
            dst.write(data, 1)

    @staticmethod
    def netcdf_to_tif_v2(nc_file, variable_name, lon_variable, lat_variable, tif_file):
        # read nc
        ds = nc.Dataset(nc_file, mode='r')

        # print(ds.dimensions)
        # var_arr = ds.variables
        # print(var_arr.keys())

        # open
        data = ds.variables[variable_name][:]

        # get coordinate
        lon = ds.variables[lon_variable][:]
        lat = ds.variables[lat_variable][:]

        custom_transform = from_origin(lon.min(), lat.max(), lon[1] - lon[0], lat[1] - lat[1])

        # populate meta data
        new_ds = rasterio.open(
            tif_file,
            'w',
            driver='GTiff',
            height=data.shape[0],
            width=data.shape[1],
            count=1,
            dtype=data.dtype,
            crs='EPSG:4326',
            transform=custom_transform,
        )

        # write
        new_ds.write(data, 1)

        # close file
        new_ds.close()
        ds.close()

    @staticmethod
    def map_to_tif(nc_file, variable_name, lon_variable, lat_variable, tif_file):
        """
        一共有M个点组成N个网格
        mesh2d_face_nodes: [N * 5]
        mesh2d_waterdepth: [time * N]
        mesh2d_node_x: [M]
        mesh2d_node_y: [M]
        `mesh2d_face_nodes` 里面存储了每个三角形网格或者四边形网格的顶点序号，和 `mesh2d_waterdepth` 是一一对应的。
        通过 `mesh2d_face_nodes` 中的顶点序号就可以从 `mesh2d_node_x`、`mesh2d_node_y` 中查询到每个顶点的坐标，
        这样就可以确定网格的形状和位置了
        """
        face_nodes_var = "mesh2d_face_nodes"
        # open nc file
        ds = nc.Dataset(nc_file, mode='r')

        waterdepth = ds.variables['mesh2d_waterdepth'][119, :]
        df_level = pd.DataFrame(waterdepth)
        df_level.columns = ['waterdepthMax']

        # read variables
        lon = ds.variables[lon_variable][:]  # 31976个点，包括重复的
        lat = ds.variables[lat_variable][:]  # 31976个点
        # 三角网格 或 四角网格
        face_nodes = ds.variables[face_nodes_var][:]  # 61309, 5
        water_depth = ds.variables[variable_name][:]  # 169, 61309
        water_depth = water_depth[15, :]  # 取第15个时间的水深数据，61309个网格

        if lon.size != lat.size:
            raise ValueError("The lon and lat variable is not the same size.")
        if face_nodes.shape[0] != water_depth.size:
            raise ValueError("The face_nodes and water_depth variable is not the same size.")

        # 创建一个二维数组来存储数据
        data_2d = np.full((face_nodes.shape[0], face_nodes.shape[0]), 0)
        new_lon = np.array([], dtype=np.float64)
        new_lat = np.array([], dtype=np.float64)
        # 读取网格
        for grid in face_nodes:
            grid = grid.compressed()
            if len(grid) > 3:
                point_lon, point_lat = Converter.calculate_quadrilateral_center(
                    [(lon[grid[0] - 1], lat[grid[0] - 1]), (lon[grid[1] - 1], lat[grid[1] - 1]),
                     (lon[grid[2] - 1], lat[grid[2] - 1]), (lon[grid[3] - 1], lat[grid[3] - 1])])
                new_lon = np.append(new_lon, point_lon)
                new_lat = np.append(new_lat, point_lat)
            else:
                point_lon, point_lat = Converter.calculate_triangle_center(
                    [(lon[grid[0] - 1], lat[grid[0] - 1]), (lon[grid[1] - 1], lat[grid[1] - 1]),
                     (lon[grid[2] - 1], lat[grid[2] - 1])])
                new_lon = np.append(new_lon, point_lon)
                new_lat = np.append(new_lat, point_lat)

        # 将一维数据填充到二维数组中
        for row in data_2d:
            for col in row:
                data_2d[row, col] = 1
        for point_lon in lon:
            for point_lat in lat:
                print(point_lon, point_lat)

        # 定义transform
        my_transform = from_origin(min(lon), max(lat), abs(lon[1] - lon[0]), abs(lat[1] - lat[0]))

        # 将二维数组保存为GeoTIFF文件
        with rasterio.open(tif_file, 'w', driver='GTiff', height=1, width=1, count=1,
                           dtype=data_2d.dtype,
                           crs='+proj=latlong', transsform=my_transform) as dst:
            dst.write(data_2d, 1)

    @staticmethod
    def calculate_triangle_center(vertices):
        """
        计算三角网格的中心点坐标
        :param vertices: 三角网格的顶点坐标列表 [(x1, y1), (x2, y2), (x3, y3)]
        :return: 中心点坐标 (x_c, y_c)
        """
        x_c = sum(vertex[0] for vertex in vertices) / 3
        y_c = sum(vertex[1] for vertex in vertices) / 3
        return x_c, y_c

    @staticmethod
    def calculate_quadrilateral_center(vertices):
        """
        计算四角网格的中心点坐标
        :param vertices: 四角网格的顶点坐标列表 [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
        :return: 中心点坐标 (x_c, y_c)
        """
        x_c = sum(vertex[0] for vertex in vertices) / 4
        y_c = sum(vertex[1] for vertex in vertices) / 4
        return x_c, y_c


def main():
    nc_file = '../../storage/Mangkhut_4_map.nc'
    tif_file = '../../storage/map.tif'
    Converter.map_to_tif(nc_file, "mesh2d_waterdepth", "mesh2d_node_x", "mesh2d_node_x", tif_file)

    # nc_file = '../../storage/Mangkhut_4_his.nc'
    # tif_file = '../../storage/his.tif'
    # Converter.netcdf_to_tif(nc_file, "velocity_magnitude", "station_x_coordinate",
    #                            "station_y_coordinate", tif_file)


if __name__ == '__main__':
    main()

# Converter.netcdf_to_tif("../../storage/Mangkhut_4_map.nc", "mesh2d_waterdepth", "mesh2d_node_x",
#                             "mesh2d_node_y", "../../storage/map.tif")

# Converter.netcdf_to_tif("../../storage/Mangkhut_4_his.nc", "velocity_magnitude", "station_x_coordinate",
#                            "station_y_coordinate", "../../storage/his2.tif")

# Converter.netcdf_to_tif1("../../storage/Mangkhut_4_his.nc", "velocity_magnitude", "station_x_coordinate",
# "station_y_coordinate","../../storage/vm.tif")

# Converter.netcdf_to_geojson("../../storage/Mangkhut_4_map.nc", "mesh2d_waterdepth", "mesh2d_node_y", ["timestep"],
# "../../storage/map.geojson")

# Converter.netcdf_to_geojson("../../storage/Mangkhut_4_his.nc", "station_x_coordinate", "station_y_coordinate",
# ["waterdepth", "waterlevel", "velocity_magnitude", "time"], "../../storage/his.geojson")

import datetime

import branca.colormap as cm
import folium
import geojson
import geopandas as gpd
import matplotlib.pyplot as plt
import netCDF4 as nc
import numpy as np
import rasterio
import xarray as xr
from rasterio.transform import from_origin
from scipy.interpolate import griddata
from shapely import MultiPoint
from shapely.geometry import Polygon

WATER_DEPTH = 'wd'


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
        with open(file=geojson_name, mode="w") as f:
            geojson.dump(geojson.FeatureCollection(geojson_features), f)

    @staticmethod
    def calculate_triangle_center(vertices):
        """
        计算三角网格的中心点坐标

        Args:
            vertices(List): 三角网格的顶点坐标列表

        Returns:
            Tuple(float64, float64): 中心点坐标

        Example:
            calculate_triangle_center([(1,2), (1,2), (1,2)])
        """
        x_c = sum(vertex[0] for vertex in vertices) / 3
        y_c = sum(vertex[1] for vertex in vertices) / 3
        return x_c, y_c

    @staticmethod
    def calculate_quadrilateral_center(vertices):
        """
        计算四角网格的中心点坐标

        Args:
            vertices(List): 四角网格的顶点坐标列表

        Returns:
            Tuple(float64, float64): 中心点坐标

        Example:
            calculate_triangle_center([(1,2), (1,2), (1,2), (1,2)])
        """
        x_c = sum(vertex[0] for vertex in vertices) / 4
        y_c = sum(vertex[1] for vertex in vertices) / 4
        return x_c, y_c

    @staticmethod
    def map_to_shp_and_html(nc_file, shp_file, html_file, time_index=15):
        """
        将nc文件转为shp并输出html

        Args:
            nc_file(String): Path and name of NetCDF file to convert.
            shp_file(String): Path and name of desired GeoJSON file output.
            html_file(String): Path and name of desired HTML file output.
            time_index(int): mesh2d_waterdepth的时间序列，范围为[0, 168]

        Example:
            map_to_shp_and_html('map.nc', 'water_depth.shp', 'water_depth.html')
        """
        dataset = nc.Dataset(nc_file)

        # 获取经纬度和数据
        lon = dataset.variables['mesh2d_node_x'][:]
        lat = dataset.variables['mesh2d_node_y'][:]
        face_nodes = dataset.variables['mesh2d_face_nodes'][:]
        water_depth = dataset.variables['mesh2d_waterdepth'][:]  # 169, 61309
        water_depth = water_depth[time_index, :]  # 取第15个时间的水深数据，61309个网格

        # 判断是三角网格还是四角网格，并生成相应的几何图形
        geometries = []
        water_depth_arr = []
        for i, face_node in enumerate(face_nodes):
            node = face_node.compressed()
            if len(node) == 3:
                poly = Polygon([
                    (lon[node[0] - 1], lat[node[0] - 1]), (lon[node[1] - 1], lat[node[1] - 1]),
                    (lon[node[2] - 1], lat[node[2] - 1])
                ])
            elif len(node) == 4:
                sorted_nodes = sort_vertices(
                    np.array([lon[node[0] - 1], lon[node[1] - 1], lon[node[2] - 1], lon[node[3] - 1]]),
                    np.array([lat[node[0] - 1], lat[node[1] - 1], lat[node[2] - 1], lat[node[3] - 1]])
                )
                poly = Polygon([
                    (lon[node[sorted_nodes[0]] - 1], lat[node[sorted_nodes[0]] - 1]),
                    (lon[node[sorted_nodes[1]] - 1], lat[node[sorted_nodes[1]] - 1]),
                    (lon[node[sorted_nodes[2]] - 1], lat[node[sorted_nodes[2]] - 1]),
                    (lon[node[sorted_nodes[3]] - 1], lat[node[sorted_nodes[3]] - 1])
                ])
            else:
                continue

            geometries.append(poly)
            water_depth_arr.append(water_depth[i])

        # 创建 GeoDataFrame
        gdf = gpd.GeoDataFrame({'geometry': geometries, WATER_DEPTH: water_depth_arr})

        # 保存为 .shp 文件
        gdf.to_file(shp_file)

        Converter.visualize_shp_interactive(gdf, html_file)

    @staticmethod
    def shp_to_tif(shp_file, tif_file, grid_size=2000):
        """
        将shp文件转为tif

        Args:
            shp_file(String): shp文件路径
            tif_file(String): 转成的tif文件路径
            grid_size(int): Default 2000

        Example:
            shp_to_tif('water_depth.shp', 'water_depth.tif')
        """
        # 读取SHP文件
        gdf = gpd.read_file(shp_file)

        # 提取几何中心点和属性值
        face_centers = np.array([geom.centroid.coords[0] for geom in gdf.geometry])
        values = gdf[WATER_DEPTH].values

        # 定义栅格网格
        x_min, x_max = face_centers[:, 0].min(), face_centers[:, 0].max()
        y_min, y_max = face_centers[:, 1].min(), face_centers[:, 1].max()
        grid_x, grid_y = np.mgrid[x_min:x_max:complex(grid_size), y_min:y_max:complex(grid_size)]

        # 使用griddata进行插值
        grid_z = griddata(face_centers, values, (grid_x, grid_y), method='linear')

        # 创建 GeoTIFF 文件
        transform = from_origin(x_min, y_max, (x_max - x_min) / grid_size, (y_max - y_min) / grid_size)
        new_dataset = rasterio.open(
            fp=tif_file,
            mode='w',
            driver='GTiff',
            height=grid_z.shape[0],
            width=grid_z.shape[1],
            count=1,
            dtype=grid_z.dtype,
            crs='EPSG:4326',
            transform=transform,
        )

        new_dataset.write(grid_z, 1)
        new_dataset.close()

    @staticmethod
    def visualize_shp(shp_file, png_file):
        """
        可视化shp文件，并导出为png

        Args:
            shp_file(String): shp文件路径
            png_file(String): png文件的输出路径

        Returns:

        Example:
            visualize_shp('water_depth.shp', 'water_depth.png')
        """
        start = datetime.datetime.now()
        # 读取 .shp 文件
        gdf = gpd.read_file(shp_file)

        # 创建一个颜色映射，viridis 是默认的颜色映射之一，通常用于绘制热图、等值线图等数据可视化。
        # 可选的颜色映射：colormaps = ['viridis', 'plasma', 'inferno', 'magma', 'cividis', 'Blues', 'RdYlBu', 'rainbow']
        cmap = plt.colormaps.get_cmap('viridis')

        # 归一化数据值，将任意范围的数据线性映射到 [0, 1] 之间
        norm = plt.Normalize(vmin=gdf[WATER_DEPTH].min(), vmax=gdf[WATER_DEPTH].max())

        # 绘制图形。figsize: 整个图表的宽和高，以英寸为单位
        fig, ax = plt.subplots(1, 1, figsize=(10, 10))
        gdf.plot(column=WATER_DEPTH, ax=ax, legend=True, cmap=cmap, norm=norm)

        # 添加标题和坐标轴标签
        ax.set_title('Water Depth Visualization')
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')

        # 显示图形
        # plt.show()
        # dpi：图像分辨率，低 dpi（如 72 或 100），高 dpi（如 300 或 600）
        plt.savefig(png_file, dpi=300)

        end = datetime.datetime.now()
        execution_time = end - start
        print(f"制Png图耗时: {execution_time.total_seconds()} seconds")

    @staticmethod
    def visualize_shp_interactive(gdf, output_html):
        """
        可视化shp为可交互的地图文件

        Args:
            gdf
            output_html

        Returns:

        Example:.
            visualize_shp_interactive(gdf, 'water_depth.html')
        """
        start = datetime.datetime.now()
        # 创建 folium 地图
        m = folium.Map(location=[gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()], zoom_start=10)

        # 创建颜色映射
        colormap = cm.linear.viridis.scale(gdf[WATER_DEPTH].min(), gdf[WATER_DEPTH].max())

        # 添加多边形到地图
        for _, row in gdf.iterrows():
            sim_geo = gpd.GeoSeries(row['geometry']).simplify(tolerance=0.001)
            geo_j = sim_geo.to_json()
            geo_j = folium.GeoJson(data=geo_j, style_function=lambda x, color=colormap(row[WATER_DEPTH]): {
                'fillColor': color,
                'color': 'black',
                'weight': 0.5,
                'fillOpacity': 0.7
            })
            geo_j.add_to(m)

        # 添加颜色条
        colormap.add_to(m)

        # 保存为 HTML 文件
        m.save(output_html)

        end = datetime.datetime.now()
        execution_time = end - start
        print(f"制Html图耗时: {execution_time.total_seconds()} seconds")


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


def main():
    base_dir = '/Users/wenyanglu/Workspace/github/hydrologic_forecasting/storage'
    nc_file = base_dir + '/Mangkhut_4_map.nc'
    shp_file = base_dir + '/water_depth.shp'
    png_file = base_dir + '/water_depth.png'
    tif_file = base_dir + '/water_depth.tif'
    html_file = base_dir + '/water_depth.html'

    # Converter().visualize_shp(shp_file, png_file)
    Converter.map_to_shp_and_html(nc_file, shp_file, html_file)


if __name__ == '__main__':
    main()

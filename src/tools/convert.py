import branca.colormap as cm
import folium
import geopandas as gpd
import matplotlib.pyplot as plt
import netCDF4 as nc
import numpy as np
import rasterio
from rasterio.transform import from_origin
from scipy.interpolate import griddata
from shapely.geometry import Polygon


class Converter:

    @staticmethod
    def map_to_shp(nc_file):
        dataset = nc.Dataset(nc_file)

        # 获取经纬度和数据
        lon = dataset.variables['mesh2d_node_x'][:]
        lat = dataset.variables['mesh2d_node_y'][:]
        face_nodes = dataset.variables['mesh2d_face_nodes'][:]
        water_depth = dataset.variables['mesh2d_waterdepth'][:]  # 169, 61309
        water_depth = water_depth[15, :]  # 取第15个时间的水深数据，61309个网格

        # 判断是三角网格还是四角网格，并生成相应的几何图形
        geometries = []
        values = []

        for i, face_node in enumerate(face_nodes):
            node = face_node.compressed()
            if len(node) == 3:
                # 三角网格
                poly = Polygon([(lon[node[0] - 1], lat[node[0] - 1]), (lon[node[1] - 1], lat[node[1] - 1]),
                                (lon[node[2] - 1], lat[node[2] - 1])])
            elif len(node) == 4:
                # 四角网格
                poly = Polygon(
                    [(lon[node[0] - 1], lat[node[0] - 1]), (lon[node[1] - 1], lat[node[1] - 1]),
                     (lon[node[2] - 1], lat[node[2] - 1]), (lon[node[3] - 1], lat[node[3] - 1])])
            else:
                continue

            geometries.append(poly)
            values.append(water_depth[i])  # 假设data存储的值是索引，可以根据实际情况调整

        # 创建 GeoDataFrame
        gdf = gpd.GeoDataFrame({'geometry': geometries, 'value': values})

        # 保存为 .shp 文件
        gdf.to_file('../../storage/output.shp')

        Converter.visualize_shp_interactive(gdf, '../../storage/water-depth.html')

        # 栅格化 GeoDataFrame 并保存为 .tif 文件
        # 创建栅格数据
        # x_min, y_min, x_max, y_max = gdf.total_bounds
        # pixel_size = 0.01  # 假设像元大小为0.01度，可以根据实际情况调整
        # transform = from_origin(x_min, y_max, pixel_size, pixel_size)
        # out_shape = (int((y_max - y_min) / pixel_size), int((x_max - x_min) / pixel_size))
        #
        # raster = np.full(out_shape, -9999, dtype=np.float32)  # 初始化栅格数据
        #
        # # 手动栅格化每个多边形
        # for geom, value in zip(gdf.geometry, gdf.value):
        #     minx, miny, maxx, maxy = geom.bounds
        #     min_row = int((y_max - maxy) / pixel_size)
        #     max_row = int((y_max - miny) / pixel_size)
        #     min_col = int((minx - x_min) / pixel_size)
        #     max_col = int((maxx - x_min) / pixel_size)
        #
        #     for row in range(min_row, max_row + 1):
        #         for col in range(min_col, max_col + 1):
        #             x = x_min + col * pixel_size + pixel_size / 2
        #             y = y_max - row * pixel_size - pixel_size / 2
        #             if geom.contains(Point(x, y)):
        #                 raster[row, col] = value
        #
        # with rasterio.open(tif_file, 'w', driver='GTiff', height=out_shape[0], width=out_shape[1], count=1,
        #                    dtype='float32', crs='EPSG:4326', transform=transform) as dst:
        #     dst.write(raster, 1)

    @staticmethod
    def shp_to_tif(shp_file, tif_file, grid_size=2000):
        # 读取SHP文件
        gdf = gpd.read_file(shp_file)

        # 提取几何中心点和属性值
        face_centers = np.array([geom.centroid.coords[0] for geom in gdf.geometry])
        values = gdf['value'].values

        # 定义栅格网格
        x_min, x_max = face_centers[:, 0].min(), face_centers[:, 0].max()
        y_min, y_max = face_centers[:, 1].min(), face_centers[:, 1].max()
        grid_x, grid_y = np.mgrid[x_min:x_max:complex(grid_size), y_min:y_max:complex(grid_size)]

        # 使用griddata进行插值
        grid_z = griddata(face_centers, values, (grid_x, grid_y), method='linear')

        # 创建 GeoTIFF 文件
        transform = from_origin(x_min, y_max, (x_max - x_min) / grid_size, (y_max - y_min) / grid_size)
        new_dataset = rasterio.open(
            tif_file,
            'w',
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
    def visualize_shp(shp_file):
        # 读取 .shp 文件
        gdf = gpd.read_file(shp_file)

        # 创建一个颜色映射，viridis 是默认的颜色映射之一，通常用于绘制热图、等值线图等数据可视化。
        # cmap = plt.cm.get_cmap('viridis')
        cmap = plt.colormaps.get_cmap('viridis')

        # 归一化数据值
        norm = plt.Normalize(vmin=gdf['value'].min(), vmax=gdf['value'].max())

        # 绘制图形
        fig, ax = plt.subplots(1, 1, figsize=(10, 10))
        gdf.plot(column='value', ax=ax, legend=True, cmap=cmap, norm=norm)

        # 添加标题和坐标轴标签
        ax.set_title('Water Depth Visualization')
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')

        # 显示图形
        # plt.show()
        plt.savefig('../../storage/water_depth.png', dpi=300)

    @staticmethod
    def visualize_shp_interactive(gdf, output_html):
        # 创建 folium 地图
        m = folium.Map(location=[gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()], zoom_start=10)

        # 创建颜色映射
        colormap = cm.linear.viridis.scale(gdf['value'].min(), gdf['value'].max())

        # 添加多边形到地图
        for _, row in gdf.iterrows():
            sim_geo = gpd.GeoSeries(row['geometry']).simplify(tolerance=0.001)
            geo_j = sim_geo.to_json()
            geo_j = folium.GeoJson(data=geo_j, style_function=lambda x, color=colormap(row['value']): {
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


def main():
    shp_file = '../../storage/output.shp'
    nc_file = '../../storage/Mangkhut_4_map.nc'
    tif_file = '../../storage/map.tif'
    #
    # Converter.map_to_tif(nc_file, tif_file)
    Converter.map_to_shp(nc_file)


if __name__ == '__main__':
    main()

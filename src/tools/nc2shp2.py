# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 14:14:32 2020

@author: 84054
"""

import datetime

import geopandas as gpd
import numpy as np
import pandas as pd
from netCDF4 import Dataset
from pandas import merge
from shapely.geometry import Polygon


# filepath = 'E:\\Work\\5_python\\mandi_without\\'
# filename = '1415mandi_map.nc'
def nc2shp(input_path, output_path):
    nc_data = Dataset(input_path)
    # for i in nc_data.variables.keys():
    #     print(i)
    lon = nc_data.variables['mesh2d_node_x'][:]
    lat = nc_data.variables['mesh2d_node_y'][:]
    id_node = np.arange(1, len(lon) + 1, 1)
    temp_node = np.vstack((id_node, lon, lat))
    node = np.transpose(temp_node)

    df_node = pd.DataFrame(node)
    df_node.columns = ['id_node', 'lon', 'lat']

    face_node = nc_data.variables['mesh2d_face_nodes'][:]
    # polygons = []
    for face in face_node:
        valid_nodes = face.compressed()
        if len(valid_nodes) > 3:
            id_face = np.arange(1, len(face_node) + 1, 1)
            temp_face = np.vstack((id_face, valid_nodes[:, 0], valid_nodes[:, 1], valid_nodes[:, 2], valid_nodes[:, 3]))
            face = np.transpose(temp_face)

            node_1 = face[:, [0, 1]]
            node_2 = face[:, [0, 2]]
            node_3 = face[:, [0, 3]]
            node_4 = face[:, [0, 4]]

            face_id = np.vstack((node_1, node_2, node_3, node_4))

        else:
            valid_nodes = face

    id_face = np.arange(1, len(face_node) + 1, 1)
    temp_face = np.vstack((id_face, valid_nodes[:, 0], valid_nodes[:, 1], valid_nodes[:, 2]))
    face = np.transpose(temp_face)

    node_1 = face[:, [0, 1]]
    node_2 = face[:, [0, 2]]
    node_3 = face[:, [0, 3]]

    face_id = np.vstack((node_1, node_2, node_3))
    face_id = face_id[face_id[:, 0].argsort()]

    df_face = pd.DataFrame(face_id)
    df_face.columns = ['id_face', 'id_node']

    df_face = merge(df_face, df_node, how='right', on='id_node')
    df_face = df_face.sort_values(by='id_face')

    waterdepth = nc_data.variables['mesh2d_waterdepth'][119, :]
    df_level = pd.DataFrame(waterdepth)
    df_level.columns = ['waterdepthMax']

    df_level.insert(0, 'id_face', id_face)

    output = df_face.groupby('id_face').apply(
        lambda df: Polygon([(x, y) for x, y in zip(df['lon'], df['lat'])])).to_frame(name='geometry')
    output.insert(0, 'df_level', id_face)
    output = merge(output, df_level, how='left', on='id_face')

    output = gpd.GeoDataFrame(output, crs='EPSG:4326')

    # 导出shapefile
    # shp name = '1415mandi_max.shp'
    output.to_file(output_path, driver='ESRI Shapefile', encoding='utf-8')


def main():
    # fn_path = '/Users/wenyanglu/Workspace/github/hydrologic_forecasting/storage'
    # dir_path = '/Users/wenyanglu/Workspace/github/hydrologic_forecasting/storage'
    # f_name = fnmatch.filter(os.listdir(fn_path), '*map.nc')
    #
    # for filename in f_name:
    #     in_path = os.path.join(fn_path, filename)
    #     print(filename)
    #     # outPath = os.path.join(dirPath, filename[0:-3]+'_max.shp')
    #     out_path = os.path.join(dir_path, filename[0:-7] + '.shp')
    #     # outPath = os.path.join(dirPath, filename[0:-3]+'_fullland.shp')
    #     # outPath = os.path.join(dirPath, filename[0:-3]+'_mainland.shp')
    #     nc2shp(in_path, out_path)
    #     print(out_path)
    input_path = '/Users/wenyanglu/Workspace/github/hydrologic_forecasting/storage/Mangkhut_4_map.nc'
    output_path = '/Users/wenyanglu/Workspace/github/hydrologic_forecasting/storage/map.shp'
    nc2shp(input_path, output_path)


if __name__ == '__main__':
    start = datetime.datetime.now()

    main()

    duration = datetime.datetime.now() - start
    print('Total running time: ', duration)

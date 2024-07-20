<h1 align="center">👋 hydrologic_forecasting</h1>

## 📚 Tech Stack

- [x] [Django](https://github.com/django/django) The Web framework for perfectionists with deadlines.
- [x] [netCDF4]() Read nc file
- [x] [GeoServer](https://docs.geoserver.org/latest/en/user/installation/win_installer.html) GeoServer is an open source
  server for sharing geospatial data.

## 🗺️ Maps

| Name    | Repository Link                                | Remark                                                                  |
|---------|------------------------------------------------|-------------------------------------------------------------------------|
| cesium  | [Click me](https://github.com/CesiumGS/cesium) | An open-source JavaScript library for world-class 3D globes and maps 🌎 |
| Leaflet | [Click me](https://github.com/Leaflet/Leaflet) | 🍃 JavaScript library for mobile-friendly interactive maps 🇺🇦         |

## 💻 Frontend

+ `GeoJSON` + `GeoServer`
+ `Tif` + `GeoServer`

## 🔌 Backend

### <a href="" target="_blank" rel="noreferrer"><img src="https://cdn.worldvectorlogo.com/logos/python-5.svg" alt="Near" width="15" height="15"/></a> Python

#### [matplotlib.pyplot](https://matplotlib.org/3.5.3/api/_as_gen/matplotlib.pyplot.html)

用于绘制数据图表的一个库，它提供了一组简单且易于使用的函数，类似于 MATLAB 风格的绘图API。它是 Matplotlib
库的一部分，可以用来创建各种类型的图表，如线图、柱状图、散点图、饼图、直方图等。

#### geopandas

扩展了 Pandas 库的功能，提供了对地理空间数据的支持，使得用户能够轻松地处理、分析和可视化地理空间数据。

#### folium

Folium 是一个用于在 Python 中制作交互式地图的库，特别是基于 Leaflet.js 库构建的地图。它的主要作用是帮助用户在 Jupyter
Notebook 环境中创建和展示交互式地图，并且能够轻松地将地理空间数据添加到地图中进行可视化。

## 📆 Develop Plan

| Item | Deadline | Remark | Status |
|------|----------|--------|--------|
|      |          |        |        |
|      |          |        |        |
|      |          |        |        |

### GeoJSON data sample

GeoJSON is a format for encoding a variety of geographic data structures.

```json
{
  "type": "Feature",
  "geometry": {
    "type": "Point",
    "coordinates": [
      125.6,
      10.1
    ]
  },
  "properties": {
    "name": "Dinagat Islands"
  }
}
```

> GeoJSON supports the following geometry types: **Point**, **LineString**, **Polygon**, **MultiPoint**, *
*MultiLineString**, and **MultiPolygon**. Geometric objects with additional properties are Feature objects. Sets of
> features are contained by FeatureCollection objects.

## Requirements

Tesseract-OCR

+ Windows:

1. 下载 Tesseract-OCR 的安装程序：Tesseract GitHub Releases。
2. 运行安装程序并安装 Tesseract。
3. 安装完成后，记下安装路径（例如，C:\Program Files\Tesseract-OCR\tesseract.exe）。

+ macOS:

```shell
brew install tesseract
```

+ Linux:

```shell
sudo apt-get install tesseract-ocr
```
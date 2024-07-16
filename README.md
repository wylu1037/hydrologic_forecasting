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

## 📆 Develop Plan

+ Read nc
+ Convert nc to GeoJSON <sub>or TIF</sub>
+ Store GeoJSON <sub>or TIF</sub> to GeoServer
+ Display GeoJSON <sub>or TIF</sub> on the web side

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

## 备注

### numpy.arange

> 用于生成一个包含均匀间隔值的数组。

参数说明：

+ `start`：起始值，默认为 0。
+ `stop`：终止值（不包含）。
+ `step`：步长，默认为 1。
+ `dtype`：返回数组的数据类型，如果没有提供，则会使用输入数据的类型。

### numpy.vstack

> 用于将多个数组按垂直方向（行方向）堆叠在一起。

```python
import numpy as np

a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

# 使用vstack进行垂直堆叠
result = np.vstack((a, b))
print(result)
```

```
[[1 2 3]
 [4 5 6]]
```

### numpy.transpose

> 用于对数组的维度进行转置或排列

```python
import numpy as np

# 创建一个二维数组
a = np.array([[1, 2], [3, 4]])

# 对数组进行转置
transposed = np.transpose(a)
print(transposed)
```

```
[[1 3]
 [2 4]]
```

### pandas.merge

> 用于合并两个数据框（DataFrame）
>
参数说明

+ `right`: 要合并的另一个DataFrame。
+ `how`: 合并的方式，有以下几种：
    + `'left'`: 左连接，保留左边DataFrame的所有键。
    + `'right'`: 右连接，保留右边DataFrame的所有键。
    + `'outer'`: 外连接，保留所有键。
    + `'inner'`: 内连接，只保留两个DataFrame中都有的键。
+ `on`: 用于连接的列名。必须在两个DataFrame中都存在。
+ `left_on` 和 right_on: 左右DataFrame中用于连接的列名。
+ `left_index` 和 right_index: 使用左或右DataFrame的索引作为连接键。
+ `sort`: 是否对合并后的数据进行排序。
+ `suffixes`: 重叠列名的后缀。
+ `indicator`: 添加一列指示每行的来源。

### pandas.DataFrame

> DataFrame是pandas库中的一种数据结构，类似于电子表格或SQL表格。它是一个二维的、带有标签的数据结构，可以存储不同类型的数据（如整数、浮点数、字符串等）。

### numpy.ma.MaskedArray.compressed()

> 用于将所有未被屏蔽的数据作为一个一维数组返回。
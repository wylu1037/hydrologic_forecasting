## map.nc文件

网格水深展示：

一共有M个点组成N个网格（例如4个点组成2个三角形网格，有两个点是共用的），网格分为两类：三角形网格，四边形网格

1. `mesh2d_face_nodes`：[N*5]（N个网格，5列为该网格角点序号。若三角形网格，则第4~
   5列为-999（缺省）；若为四边形网格，则第5列为-999，若五边形（本例中没有该类网格），则无缺省）
2. `mesh2d_node_x` : [M]  (1)中对应的格点的经度
3. `mesh2d_node_y` : [M]  (1)中对应的格点的纬度
4. `mesh2d_waterdepth`: [time*N] N个网格每小时水深，单位为m

### 处理方法

`mesh2d_face_nodes` 里面存储了每个三角形网格或者四边形网格的顶点序号，和 `mesh2d_waterdepth` 是一一对应的。
通过 `mesh2d_face_nodes` 中的顶点序号就可以从 `mesh2d_node_x`、`mesh2d_node_y` 中查询到每个顶点的坐标，这样就可以确定网格的形状和位置了

## his.nc 文件

站点结果展示：S个站点

1. `station_x_coordinate`: [S] 站点经度
2. `station_y_coordinate`: [S] 站点纬度
3. `waterdepth`: [time*S] 每个站点的水深时间序列
4. `waterlevel`: [time*S] 每个站点的水位时间序列
5. `velocity_magnitude`:[time*S] 每个站点的流速序列

## 备注

是地理坐标系，`WGS1984`
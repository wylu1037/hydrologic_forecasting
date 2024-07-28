# Create your models here.
from django.db import models


class Project(models.Model):
    """
    项目方案数据
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_time = models.DateTimeField(null=True)
    forecast_period = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    type = models.IntegerField(default=0)


class MapData(models.Model):
    """
    地图网格数据
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    longitude = models.JSONField(blank=True, default=list)
    latitude = models.JSONField(blank=True, default=list)
    water_depth = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    risk = models.IntegerField(default=0)
    timestamp = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class StationData(models.Model):
    """
    站点数据
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    station_name = models.CharField(max_length=30, blank=True)
    longitude = models.FloatField()
    latitude = models.FloatField()
    water_depth = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    water_level = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    velocity_magnitude = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    timestamp = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class Rainfall(models.Model):
    """
    降水数据
    """
    station = models.CharField(max_length=10)
    datetime = models.DateTimeField()
    data = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)


class UpstreamWaterLevel(models.Model):
    """
    上游水位
    """
    station = models.CharField(max_length=10)
    datetime = models.DateTimeField()
    data = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)


class DownstreamWaterLevel(models.Model):
    """
    下游水位
    """
    station = models.CharField(max_length=10)
    datetime = models.DateTimeField()
    data = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)


class RainfallSeries(models.Model):
    """
    降雨序列
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    rainfall = models.DecimalField(max_digits=10, decimal_places=2)


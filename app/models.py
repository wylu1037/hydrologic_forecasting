# Create your models here.
from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    time_index = models.IntegerField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class MapData(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    longitude = models.JSONField(blank=True, default=list)
    latitude = models.JSONField(blank=True, default=list)
    water_depth = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    timestamp = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class StationData(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    longitude = models.FloatField()
    latitude = models.FloatField()
    water_depth = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    water_level = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    velocity_magnitude = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    timestamp = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


# 降水数据
class Rainfall(models.Model):
    station = models.CharField(max_length=10)
    datetime = models.DateTimeField()
    data = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

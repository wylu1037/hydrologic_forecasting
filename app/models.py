# Create your models here.
from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    time_index = models.IntegerField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ProjectGridData(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    longitude = models.JSONField(blank=True, default=list)
    latitude = models.JSONField(blank=True, default=list)
    water_depth = models.FloatField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

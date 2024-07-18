from django.urls import path

from app import views

urlpatterns = [
    path('v1/mapping/convert-nc-to-shp', views.convert_nc_to_shp_controller, name='convert_nc_to_shp_controller'),
]

from django.urls import path

from app import views

urlpatterns = [
    path('v1/mapping/convert-nc-to-shp', views.convert_nc_to_shp_controller, name='convert_nc_to_shp_controller'),
    path('v1/script/run', views.execute, name='run scripts'),
    path('v1/project/create', views.create_project, name='create project'),
    path('v1/water/information/import', views.import_water_information, name='import water information'),
    path('v1/water/information/list', views.water_information_list, name='list water information'),
]

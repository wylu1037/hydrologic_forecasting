from django.urls import path

from app import views

urlpatterns = [
    path('v1/map/handle', views.handle_map_controller, name='handle_map_controller'),
    path('v1/station/handle', views.handle_station_controller, name='handle_station_controller'),
    path('v1/station/export', views.export_station, name='export station'),
    path('v1/script/run', views.execute, name='run scripts'),
    path('v1/project/create', views.create_project, name='create project'),

]

from django.urls import path

from app import views

urlpatterns = [
    path('v1/ping', views.ping_controller, name='ping'),
    path('v1/map/handle', views.handle_map_controller, name='handle_map_controller'),
    path('v1/map/export', views.export_map_controller, name='export_map_controller'),
    path('v1/map/history/export', views.export_history_map_controller, name='export_history_map_controller'),
    path('v1/station/handle', views.handle_station_controller, name='handle_station_controller'),
    path('v1/station/export', views.export_station_controller, name='export station'),
    path('v1/station/history/export', views.export_history_station_controller, name='export history station'),
    path('v1/project/run', views.run_project, name='create project'),
    path('v1/project/update', views.update_project, name='update project'),
    path('v1/project/delete/<int:project_id>', views.delete_project, name='delete project'),
    path('v1/project/pagination/<int:page>/<int:size>', views.project_pagination, name='project pagination'),
    path('v1/forewarning/pagination/<int:page>/<int:size>', views.forewarning_pagination,
         name='forewarning pagination'),
    path('v1/station/representation', views.representation_station_controller,
         name='representation_station_controller'),
    path('v1/station/trend/<str:name>', views.trend_station_controller, name='trend_station_controller'),
    path('v1/water/information/latest', views.latest_water_information, name='latest_water_information'),
]

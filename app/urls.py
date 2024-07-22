from django.urls import path

from app import views

urlpatterns = [
    path('v1/map/handle', views.handle_map_controller, name='handle_map_controller'),
    path('v1/script/run', views.execute, name='run scripts'),
    path('v1/project/create', views.create_project, name='create project'),
]

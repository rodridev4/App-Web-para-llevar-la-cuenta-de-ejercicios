from django.urls import path
from . import views

urlpatterns = [
    # Ruta principal (Historial y Crear)
    path('', views.tracker_view, name='tracker'), 
    
    # Ruta de detalle (Editar y Borrar)
    path('workout/<int:workout_id>/', views.workout_detail, name='workout_detail'),
]
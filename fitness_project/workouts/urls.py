from django.urls import path
from . import views

urlpatterns = [
    path("", views.tracker_view, name="tracker"),
    path("workout/<int:workout_id>/", views.workout_detail, name="workout_detail"),
]

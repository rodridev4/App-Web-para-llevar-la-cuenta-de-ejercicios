from django.db import models

class Workout(models.Model):
    """
    Modelo que representa un ejercicio registrado.
    """
    # Identificador del usuario
    user_id = models.CharField(max_length=255, default='anonymous')
    
    # Nombre del ejercicio
    exercise_name = models.CharField(max_length=100)
    
    # Cantidad de series
    sets = models.IntegerField()
    
    # Cantidad de repeticiones o descripción de carga
    reps = models.CharField(max_length=50)
    
    # Fecha y hora de creación
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'workouts'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.exercise_name} ({self.created_at})"
from django.db import models
from django.utils import timezone


class Workout(models.Model):
    """
    Modelo optimizado para registrar ejercicios.
    """

    user_id = models.CharField(max_length=255, db_index=True, default="public-user")

    exercise_name = models.CharField(max_length=100, db_index=True)

    sets = models.PositiveIntegerField()

    reps = models.CharField(max_length=100)

    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = "workouts"

        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["exercise_name"]),
            models.Index(fields=["user_id", "created_at"]),
        ]

    def __str__(self):
        return f"{self.exercise_name} ({self.created_at})"

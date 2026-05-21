from django.db import models
from django.conf import settings

class Exercise(models.Model):
    exercise_name = models.CharField(max_length=100)
    exercise_type = models.CharField(max_length=50, blank=True, null=True)
    target_muscle_group = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.exercise_name

class GymSession(models.Model):
    profile = models.ForeignKey('users.Profile', on_delete=models.CASCADE, related_name="sessions")
    session_name = models.CharField(max_length=100, blank=True, null=True)
    session_date = models.DateTimeField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.session_name or 'Session'} - {self.session_date.date()}"

class SessionExercise(models.Model):
    session = models.ForeignKey(GymSession, on_delete=models.CASCADE, related_name="session_exercises")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    order_number = models.PositiveIntegerField(default=1)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['order_number']

    def __str__(self):
        return f"{self.exercise.exercise_name} in {self.session}"

class ExerciseSet(models.Model):
    session_exercise = models.ForeignKey(SessionExercise, on_delete=models.CASCADE, related_name="sets")
    set_number = models.PositiveIntegerField()
    reps = models.IntegerField(blank=True, null=True)
    weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    duration_seconds = models.IntegerField(blank=True, null=True)
    distance_metres = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['set_number']

class Goal(models.Model):
    profile = models.ForeignKey('users.Profile', on_delete=models.CASCADE, related_name="goals")
    exercise = models.ForeignKey(Exercise, on_delete=models.SET_NULL, null=True, blank=True)
    goal_type = models.CharField(max_length=50)
    target_value = models.DecimalField(max_digits=10, decimal_places=2)
    target_date = models.DateField(blank=True, null=True)
    achieved = models.BooleanField(default=False)
    achieved_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.goal_type} for {self.profile.nickname}"

class Reward(models.Model):
    profile = models.ForeignKey('users.Profile', on_delete=models.CASCADE, related_name="rewards")
    goal = models.ForeignKey(Goal, on_delete=models.SET_NULL, null=True, blank=True)
    reward_name = models.CharField(max_length=100)
    reward_description = models.TextField(blank=True, null=True)
    points_awarded = models.IntegerField(default=0)
    awarded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reward_name} - {self.profile.nickname}"

class SavedWorkout(models.Model):
    profile = models.ForeignKey('users.Profile', on_delete=models.CASCADE, related_name="saved_workouts")
    workout_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.workout_name

class SavedWorkoutExercise(models.Model):
    saved_workout = models.ForeignKey(SavedWorkout, on_delete=models.CASCADE, related_name="exercises")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    order_number = models.PositiveIntegerField(default=1)
    target_sets = models.IntegerField(blank=True, null=True)
    target_reps = models.IntegerField(blank=True, null=True)
    target_weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    target_duration_seconds = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ['order_number']
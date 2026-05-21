from django.contrib import admin
from .models import (
    Exercise, GymSession, SessionExercise, ExerciseSet, 
    Goal, Reward, SavedWorkout, SavedWorkoutExercise
)

class ExerciseSetInline(admin.TabularInline):
    model = ExerciseSet
    extra = 1

class SessionExerciseInline(admin.StackedInline):
    model = SessionExercise
    extra = 1
    show_change_link = True

@admin.register(GymSession)
class GymSessionAdmin(admin.ModelAdmin):
    list_display = ('session_name', 'profile', 'session_date', 'created_at')
    list_filter = ('session_date', 'profile')
    inlines = [SessionExerciseInline]

@admin.register(SessionExercise)
class SessionExerciseAdmin(admin.ModelAdmin):
    list_display = ('exercise', 'session', 'order_number')
    inlines = [ExerciseSetInline]

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('exercise_name', 'exercise_type', 'target_muscle_group')
    search_fields = ('exercise_name', 'target_muscle_group')

class SavedWorkoutExerciseInline(admin.TabularInline):
    model = SavedWorkoutExercise
    extra = 1

@admin.register(SavedWorkout)
class SavedWorkoutAdmin(admin.ModelAdmin):
    list_display = ('workout_name', 'profile', 'created_at')
    inlines = [SavedWorkoutExerciseInline]

admin.site.register(Goal)
admin.site.register(Reward)
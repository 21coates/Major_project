from django.urls import path
from . import views

app_name = "my_app"

urlpatterns = [
    path("", views.homepage, name="home"),
    path("create_gym_session/", views.create_gym_session, name="create_gym_session"),
    path("workouts/", views.workouts, name="workouts"),
    path("workouts/<int:session_id>/", views.workout_detail, name="workout_detail"),
    path("leaderboard/", views.leaderboard, name="leaderboard"),
]
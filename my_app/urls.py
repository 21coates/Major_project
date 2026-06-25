from django.urls import path
from . import views

app_name = "my_app"

urlpatterns = [
    path("", views.homepage, name="home"),
    path("create_gym_session/", views.create_gym_session, name="create_gym_session"),
    path("workouts/", views.workouts, name="workouts"),
    path("workouts/<int:session_id>/", views.workout_detail, name="workout_detail"),
    path("leaderboard/bench/", views.leaderboard_bench, name="leaderboard_bench"),
    path("leaderboard/squat/", views.leaderboard_squat, name="leaderboard_squat"),
    path("leaderboard/deadlift/", views.leaderboard_deadlift, name="leaderboard_deadlift"),
    path("leaderboard/powerlifting/", views.leaderboard_powerlifting, name="leaderboard_powerlifting"),
    path("leaderboard/xp/", views.leaderboard_xp, name="leaderboard_xp"),
    path("create_exercise/", views.create_exercise, name="create_exercise"),
]
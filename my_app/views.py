from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import get_user_model
from users.models import Profile
from django.db.models import Count

from .models import Exercise, GymSession, SessionExercise, ExerciseSet


@login_required(login_url="users:login")
def create_gym_session(request):
    exercises = Exercise.objects.all().order_by("exercise_name")

    # Handle new exercise creation
    if request.method == "POST" and request.POST.get("add_exercise"):
        new_name = request.POST.get("new_exercise_name")
        new_muscle = request.POST.get("new_exercise_muscle")
        if new_name:
            Exercise.objects.create(
                exercise_name=new_name,
                target_muscle_group=new_muscle
            )
            messages.success(request, f"Exercise '{new_name}' added!")
            return redirect('my_app:create_gym_session')

    if request.method == "POST" and not request.POST.get("add_exercise"):
        session_name = request.POST.get("session_name")
        selected_exercises = request.POST.getlist("exercise_id")

        with transaction.atomic():
            gym_session = GymSession.objects.create(
                profile=request.user.profile,
                session_name=session_name,
                session_date=timezone.now(),  # Automatically set current date/time
            )

            for index, exercise_id in enumerate(selected_exercises, start=1):
                if not exercise_id:
                    continue

                exercise = Exercise.objects.get(id=exercise_id)

                session_exercise = SessionExercise.objects.create(
                    session=gym_session,
                    exercise=exercise,
                    order_number=index,
                )

                reps = request.POST.get(f"reps_{index}")
                weight = request.POST.get(f"weight_{index}")

                ExerciseSet.objects.create(
                    session_exercise=session_exercise,
                    set_number=1,
                    reps=reps or None,
                    weight=weight or None,
                    completed=False,
                )

        return redirect('my_app:home')

    return render(request, "my_app/create_gym_session.html", {
        "exercises": exercises
    })


@login_required(login_url="users:login")
def homepage(request):
    return render(request, "my_app/home.html")


@login_required(login_url="users:login")
def workouts(request):
    sessions = request.user.profile.sessions.order_by('-session_date')
    return render(request, "my_app/workouts.html", {"sessions": sessions})


@login_required(login_url="users:login")
def workout_detail(request, session_id):
    session = get_object_or_404(request.user.profile.sessions, id=session_id)
    session_exercises = session.session_exercises.select_related('exercise').prefetch_related('sets')
    return render(request, "my_app/workout_detail.html", {"session": session, "session_exercises": session_exercises})


def leaderboard(request):
    leaderboard_data = Profile.objects.annotate(workout_count=Count('sessions')).order_by('-workout_count', 'nickname')
    return render(request, 'my_app/leaderboard.html', {'leaderboard': leaderboard_data})
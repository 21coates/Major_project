from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import get_user_model
from users.models import Profile
from django.db.models import Count, Max, Q
from itertools import groupby

from .models import Exercise, GymSession, SessionExercise, ExerciseSet


@login_required(login_url="users:login")
def create_gym_session(request):
    # Ensure staple exercises exist
    staple_exercises = [
        ("Bench Press", "Chest"),
        ("Squat", "Legs"),
        ("Deadlift", "Back")
    ]
    for name, muscle in staple_exercises:
        Exercise.objects.get_or_create(exercise_name=name, defaults={"target_muscle_group": muscle})
    exercises = Exercise.objects.all().order_by("target_muscle_group", "exercise_name")

    # build grouped list of (muscle_group, exercises_list)
    def _muscle_key(e):
        return e.target_muscle_group or "Uncategorized"
    grouped = []
    for muscle, grp in groupby(exercises, key=_muscle_key):
        grouped.append((muscle, list(grp)))

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

        if not selected_exercises:
            messages.error(request, "Please select at least one exercise for the session.")
            return render(request, "my_app/create_gym_session.html", {
                "exercises": exercises,
                "grouped_exercises": grouped,
            })

        with transaction.atomic():
            gym_session = GymSession.objects.create(
                profile=request.user.profile,
                session_name=session_name,
                session_date=timezone.now(),  # Automatically set current date/time
            )

            for order_number, exercise_id in enumerate(selected_exercises, start=1):
                if not exercise_id:
                    continue

                exercise = Exercise.objects.get(id=exercise_id)

                session_exercise = SessionExercise.objects.create(
                    session=gym_session,
                    exercise=exercise,
                    order_number=order_number,
                )

                reps = request.POST.get(f"reps_{exercise_id}")
                weight = request.POST.get(f"weight_{exercise_id}")

                ExerciseSet.objects.create(
                    session_exercise=session_exercise,
                    set_number=1,
                    reps=reps or None,
                    weight=weight or None,
                    completed=False,
                )

        return redirect('my_app:home')

    return render(request, "my_app/create_gym_session.html", {
        "exercises": exercises,
        "grouped_exercises": grouped,
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


# def leaderboard(request):
#     leaderboard_data = Profile.objects.annotate(workout_count=Count('sessions')).order_by('-workout_count', 'nickname')
#     return render(request, 'my_app/leaderboard.html', {'leaderboard': leaderboard_data})


@login_required(login_url="users:login")
def create_exercise(request):
    edit_id = None
    if request.method == "POST":
        if request.POST.get("edit_id"):
            ex_id = request.POST.get("edit_id")
            ex = get_object_or_404(Exercise, id=ex_id)
            if request.POST.get("delete_exercise") == '1':
                ex.delete()
                messages.success(request, "Exercise removed!")
                return redirect('my_app:create_exercise')
            elif request.POST.get("edit_exercise") == '1':
                # Enter edit mode for this row
                edit_id = ex_id
            else:
                ex.exercise_name = request.POST.get("exercise_name")
                ex.target_muscle_group = request.POST.get("target_muscle_group")
                ex.save()
                messages.success(request, f"Exercise '{ex.exercise_name}' updated!")
                return redirect('my_app:create_exercise')
        else:
            # Creating a new exercise
            name = request.POST.get("exercise_name")
            muscle = request.POST.get("target_muscle_group")
            if name:
                Exercise.objects.create(exercise_name=name, target_muscle_group=muscle)
                messages.success(request, f"Exercise '{name}' added!")
                return redirect('my_app:create_exercise')
            else:
                messages.error(request, "Exercise name is required.")
    exercises = Exercise.objects.all().order_by('target_muscle_group', 'exercise_name')
    grouped = []
    def _muscle_key(e):
        return e.target_muscle_group or "Uncategorized"
    from itertools import groupby
    for muscle, grp in groupby(exercises, key=_muscle_key):
        grouped.append((muscle, list(grp)))
    return render(request, "my_app/create_exercise.html", {"exercises": exercises, "grouped_exercises": grouped, "edit_id": edit_id})


def leaderboard_bench(request):
    return _leaderboard_lift(request, 'Bench Press')
def leaderboard_squat(request):
    return _leaderboard_lift(request, 'Squat')
def leaderboard_deadlift(request):
    return _leaderboard_lift(request, 'Deadlift')

def _leaderboard_lift(request, lift_name):
    # 1RM, 3RM, 5RM for the given lift
    rep_targets = [1, 3, 5]
    leaderboards = {}
    for rep in rep_targets:
        sets = ExerciseSet.objects.filter(
            session_exercise__exercise__exercise_name__iexact=lift_name,
            reps=rep
        ).values(
            'session_exercise__session__profile__nickname',
            'session_exercise__session__profile__id'
        ).annotate(
            max_weight=Max('weight')
        ).order_by('-max_weight')
        leaderboards[rep] = sets
    return render(request, 'my_app/leaderboard_lift.html', {
        'lift_name': lift_name,
        'leaderboards': leaderboards
    })
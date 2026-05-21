from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect
from django.utils.dateparse import parse_datetime
from django.contrib import messages

from .models import Exercise, GymSession, SessionExercise, ExerciseSet


@login_required(login_url="users:login")
def create_gym_session(request):
    exercises = Exercise.objects.all().order_by("exercise_name")

    if request.method == "POST":
        session_name = request.POST.get("session_name")
        session_date = request.POST.get("session_date")
        notes = request.POST.get("notes")

        selected_exercises = request.POST.getlist("exercise_id")

        if not session_date:
            messages.error(request, "Please select a session date and time.")
            return render(request, "my_app/create_gym_session.html", {
                "exercises": exercises
            })

        with transaction.atomic():
            gym_session = GymSession.objects.create(
                profile=request.user.profile,
                session_name=session_name,
                session_date=parse_datetime(session_date),
                notes=notes,
            )

            for index, exercise_id in enumerate(selected_exercises, start=1):
                if not exercise_id:
                    continue

                exercise = Exercise.objects.get(id=exercise_id)

                session_exercise = SessionExercise.objects.create(
                    session=gym_session,
                    exercise=exercise,
                    order_number=index,
                    notes=request.POST.get(f"exercise_notes_{index}", "")
                )

                reps_list = request.POST.getlist(f"reps_{index}")
                weight_list = request.POST.getlist(f"weight_{index}")

                for set_index, reps in enumerate(reps_list, start=1):
                    weight = weight_list[set_index - 1] if set_index - 1 < len(weight_list) else None

                    ExerciseSet.objects.create(
                        session_exercise=session_exercise,
                        set_number=set_index,
                        reps=reps or None,
                        weight=weight or None,
                        completed=False,
                    )

        messages.success(request, "Gym session created successfully.")
        return redirect("my_app:create_gym_session")

    return render(request, "my_app/create_gym_session.html", {
        "exercises": exercises
    })
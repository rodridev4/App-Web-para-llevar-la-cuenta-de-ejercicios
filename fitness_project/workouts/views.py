from django.shortcuts import render
from .models import Workout
from django.http import JsonResponse, Http404
import json
import datetime
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def tracker_view(request):
    default_user = "public-user"

    if request.method == "GET":

        workouts = Workout.objects.all().order_by("-created_at")

        default_exercises = [
            "Flexiones",
            "Abdominales",
            "Burpees",
            "Mancuernas",
            "Sentadillas",
        ]
        saved_exercises = Workout.objects.values_list(
            "exercise_name", flat=True
        ).distinct()
        all_exercises = sorted(list(set(default_exercises + list(saved_exercises))))

        workouts_by_date = {}
        weekly_groups = {}

        for workout in workouts:
            local_date = timezone.localtime(workout.created_at).date()

            if local_date not in workouts_by_date:
                workouts_by_date[local_date] = []
            workouts_by_date[local_date].append(workout)

            start_week = local_date - datetime.timedelta(days=local_date.weekday())

            if start_week not in weekly_groups:
                weekly_groups[start_week] = {}

            name = workout.exercise_name
            total = 0
            try:
                clean = workout.reps.replace(",", " ").lower()
                nums = [int(s) for s in clean.split() if s.isdigit()]
                if len(nums) > 1:
                    total = sum(nums)
                elif len(nums) == 1:
                    total = nums[0] * workout.sets
                else:
                    total = workout.sets
            except:
                total = 0

            weekly_groups[start_week][name] = (
                weekly_groups[start_week].get(name, 0) + total
            )

        sorted_workouts = dict(sorted(workouts_by_date.items(), reverse=True))

        weekly_summaries = []
        for start_date in sorted(weekly_groups.keys(), reverse=True):
            end_date = start_date + datetime.timedelta(days=6)
            weekly_summaries.append(
                {
                    "start": start_date,
                    "end": end_date,
                    "stats": weekly_groups[start_date],
                }
            )

        context = {
            "workouts_by_date": sorted_workouts,
            "exercises_list": all_exercises,
        }

        return render(request, "workouts/tracker.html", context)

    if request.method == "POST":
        try:
            data = json.loads(request.body)

            new_workout = Workout.objects.create(
                user_id=default_user,
                exercise_name=data.get("exercise_name"),
                sets=int(data.get("sets")),
                reps=data.get("reps"),
            )

            date_str = data.get("date")
            current_time = timezone.localtime(timezone.now()).time()

            if date_str:
                chosen_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                final_dt = datetime.datetime.combine(chosen_date, current_time)
            else:
                final_dt = datetime.datetime.combine(timezone.localdate(), current_time)

            if timezone.is_naive(final_dt):
                final_dt = timezone.make_aware(final_dt)

            new_workout.created_at = final_dt
            new_workout.save()

            return JsonResponse({"success": True, "id": new_workout.id}, status=201)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=400)


@csrf_exempt
def workout_detail(request, workout_id):
    try:
        workout = Workout.objects.get(pk=workout_id)
    except Workout.DoesNotExist:
        raise Http404("No existe.")

    if request.method == "PUT":
        try:
            data = json.loads(request.body)
            workout.exercise_name = data.get("exercise_name", workout.exercise_name)
            if data.get("sets"):
                workout.sets = int(data.get("sets"))
            workout.reps = data.get("reps", workout.reps)

            date_str = data.get("date")
            if date_str:
                chosen_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                original_time = timezone.localtime(workout.created_at).time()
                final_dt = datetime.datetime.combine(chosen_date, original_time)
                if timezone.is_naive(final_dt):
                    final_dt = timezone.make_aware(final_dt)
                workout.created_at = final_dt

            workout.save()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=400)

    elif request.method == "DELETE":
        workout.delete()
        return JsonResponse({"success": True}, status=204)

    return JsonResponse({"success": False}, status=405)

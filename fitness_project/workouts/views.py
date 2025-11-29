from django.shortcuts import render
from .models import Workout
from django.http import JsonResponse, Http404
import json
import datetime
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt 
def tracker_view(request):
    # GET: Mostrar historial y Cargar Lista de Ejercicios
    if request.method == 'GET':
        user_id = 'django-demo'
        workouts = Workout.objects.filter(user_id=user_id).order_by('-created_at')
        
        # 1. LOGICA DE LISTA DE EJERCICIOS INTELIGENTE
        # Lista base predeterminada
        default_exercises = ['Flexiones', 'Abdominales', 'Burpees', 'Mancuernas', 'Sentadillas']
        
        # Obtener nombres únicos que ya se han guardado en la base de datos
        saved_exercises = Workout.objects.filter(user_id=user_id).values_list('exercise_name', flat=True).distinct()
        
        # Combinar, eliminar duplicados y ordenar alfabéticamente
        all_exercises = sorted(list(set(default_exercises + list(saved_exercises))))

        # 2. Lógica del Historial
        today = timezone.localdate()
        start_week = today - datetime.timedelta(days=today.weekday()) 
        end_week = start_week + datetime.timedelta(days=6) 
        
        workouts_by_date = {}
        weekly_summary = {}

        for workout in workouts:
            local_dt = timezone.localtime(workout.created_at)
            local_date = local_dt.date()
            
            if local_date not in workouts_by_date:
                workouts_by_date[local_date] = []
            workouts_by_date[local_date].append(workout)
            
            if start_week <= local_date <= end_week:
                name = workout.exercise_name
                total = 0
                try:
                    clean = workout.reps.replace(',', ' ').lower()
                    nums = [int(s) for s in clean.split() if s.isdigit()]
                    if len(nums) > 1: total = sum(nums)
                    elif len(nums) == 1: total = nums[0] * workout.sets
                    else: total = workout.sets
                except: total = 0
                weekly_summary[name] = weekly_summary.get(name, 0) + total

        sorted_workouts = dict(sorted(workouts_by_date.items(), reverse=True))

        context = {
            'workouts_by_date': sorted_workouts,
            'weekly_summary': weekly_summary,
            'exercises_list': all_exercises, 
            'user_id': user_id,
            'week_start': start_week,
            'week_end': end_week,
        }
        return render(request, 'workouts/tracker.html', context)

    # POST: Guardar
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'JSON inválido'}, status=400)

        exercise_name = data.get('exercise_name')
        try:
            sets = int(data.get('sets'))
        except:
             return JsonResponse({'success': False, 'message': 'Series inválidas.'}, status=400)
        reps = data.get('reps')
        date_str = data.get('date')
        user_id = data.get('user_id', 'django-demo') 

        if exercise_name and sets and reps:
            try:
                new_workout = Workout.objects.create(
                    user_id=user_id,
                    exercise_name=exercise_name,
                    sets=sets,
                    reps=reps
                )

                current_time_local = timezone.localtime(timezone.now()).time()
                if date_str:
                    chosen_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                    final_dt = datetime.datetime.combine(chosen_date, current_time_local)
                else:
                    final_dt = datetime.datetime.combine(timezone.localdate(), current_time_local)
                
                if timezone.is_naive(final_dt):
                    final_dt = timezone.make_aware(final_dt)
                
                new_workout.created_at = final_dt
                new_workout.save()

                return JsonResponse({'success': True, 'id': new_workout.id, 'message': 'Guardado'}, status=201)
            except Exception as e:
                return JsonResponse({'success': False, 'message': str(e)}, status=500)
        
        return JsonResponse({'success': False, 'message': 'Faltan datos.'}, status=400)

@csrf_exempt
def workout_detail(request, workout_id):
    # ... (Lógica de editar/borrar)
    try:
        workout = Workout.objects.get(pk=workout_id)
    except Workout.DoesNotExist:
        raise Http404("No existe.")
    
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            workout.exercise_name = data.get('exercise_name', workout.exercise_name)
            if data.get('sets'): workout.sets = int(data.get('sets'))
            workout.reps = data.get('reps', workout.reps)
            date_str = data.get('date')
            if date_str:
                chosen_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                original_time = timezone.localtime(workout.created_at).time()
                final_dt = datetime.datetime.combine(chosen_date, original_time)
                if timezone.is_naive(final_dt):
                    final_dt = timezone.make_aware(final_dt)
                workout.created_at = final_dt
            workout.save()
            return JsonResponse({'success': True, 'message': 'Actualizado.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

    elif request.method == 'DELETE':
        workout.delete()
        return JsonResponse({'success': True, 'message': 'Eliminado.'}, status=204)
    
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)
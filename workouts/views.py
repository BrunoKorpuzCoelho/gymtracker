import json
import calendar
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils import timezone
from django.db.models import Avg, Max

from .models import (
    WorkoutPlan, ExerciseTemplate, WorkoutSession,
    ExerciseLog, BodyWeightLog, UserProfile,
)
from .forms import RegisterForm, LoginForm, BodyWeightForm, ProfileForm


# ---------------------------------------------------------------------------
# Auth views
# ---------------------------------------------------------------------------

def register_view(request):
    if request.user.is_authenticated:
        return redirect('calendar')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.get_or_create(user=user)
            login(request, user)
            return redirect('calendar')
    else:
        form = RegisterForm()
    return render(request, 'workouts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('calendar')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
    else:
        form = LoginForm()
    return render(request, 'workouts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


# ---------------------------------------------------------------------------
# Calendar / Home view
# ---------------------------------------------------------------------------

@login_required
@ensure_csrf_cookie
def calendar_view(request):
    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    cal = calendar.Calendar(firstweekday=0)  # Monday first
    month_days = cal.monthdayscalendar(year, month)
    month_name = calendar.month_name[month]

    # Get all sessions for this month
    sessions = WorkoutSession.objects.filter(
        user=request.user,
        date__year=year,
        date__month=month,
    ).select_related('workout_plan')

    session_map = {}
    for s in sessions:
        session_map[s.date.day] = {
            'color': s.workout_plan.color if s.workout_plan else '#666',
            'name': s.workout_plan.name if s.workout_plan else 'Custom',
        }

    # Plans for today's workout
    plans = list(WorkoutPlan.objects.all().values('id', 'name', 'day_of_week', 'color', 'tag'))
    today_plan = None
    if today.weekday() < 5:
        today_plan = WorkoutPlan.objects.filter(day_of_week=today.weekday()).first()

    # Previous / next month
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1
    if month == 12:
        next_year, next_month = year + 1, 1
    else:
        next_year, next_month = year, month + 1

    context = {
        'today': today,
        'year': year,
        'month': month,
        'month_name': month_name,
        'month_days': month_days,
        'session_map': session_map,
        'plans': plans,
        'today_plan': today_plan,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
    }
    return render(request, 'workouts/calendar.html', context)


# ---------------------------------------------------------------------------
# Workout session view
# ---------------------------------------------------------------------------

@login_required
@ensure_csrf_cookie
def workout_view(request, plan_id, session_date=None):
    plan = get_object_or_404(WorkoutPlan, pk=plan_id)
    workout_date = date.today()
    if session_date:
        try:
            workout_date = date.fromisoformat(session_date)
        except ValueError:
            workout_date = date.today()

    # Get or create session
    session, _ = WorkoutSession.objects.get_or_create(
        user=request.user,
        workout_plan=plan,
        date=workout_date,
    )

    exercises = plan.exercises.all()

    # Existing logs for this session
    existing_logs = ExerciseLog.objects.filter(session=session).select_related('exercise_template')
    log_map = {}
    for log in existing_logs:
        key = f"{log.exercise_template_id}_{log.set_number}"
        log_map[key] = {
            'weight': float(log.weight),
            'reps': log.reps,
            'difficulty': log.difficulty,
        }

    # Find previous session for the same plan (for progressive overload hints)
    prev_session = (
        WorkoutSession.objects
        .filter(user=request.user, workout_plan=plan, date__lt=workout_date)
        .order_by('-date')
        .first()
    )
    prev_logs = {}
    overload_hints = {}
    if prev_session:
        for log in ExerciseLog.objects.filter(session=prev_session):
            key = f"{log.exercise_template_id}_{log.set_number}"
            prev_logs[key] = {
                'weight': float(log.weight),
                'reps': log.reps,
                'difficulty': log.difficulty,
            }

        # Compute overload hints: if ALL sets of an exercise were 'easy', suggest increase
        for ex in exercises:
            ex_logs = [
                l for l in ExerciseLog.objects.filter(
                    session=prev_session, exercise_template=ex
                )
            ]
            if ex_logs and all(l.difficulty == 'easy' for l in ex_logs):
                max_weight = max(float(l.weight) for l in ex_logs)
                overload_hints[ex.id] = {
                    'message': 'Increase weight! All sets were easy last time.',
                    'prev_max': max_weight,
                }
            elif ex_logs and any(l.difficulty == 'easy' for l in ex_logs):
                overload_hints[ex.id] = {
                    'message': 'Some sets were easy — consider a small increase.',
                    'prev_max': max(float(l.weight) for l in ex_logs),
                }

    context = {
        'plan': plan,
        'session': session,
        'exercises': exercises,
        'workout_date': workout_date,
        'log_map': json.dumps(log_map),
        'prev_logs': json.dumps(prev_logs),
        'overload_hints': json.dumps(overload_hints),
    }
    return render(request, 'workouts/workout.html', context)


# ---------------------------------------------------------------------------
# API: Save exercise log (AJAX)
# ---------------------------------------------------------------------------

@login_required
@require_POST
def save_exercise_log(request):
    """Save or update a single set log via AJAX."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    session_id = data.get('session_id')
    exercise_id = data.get('exercise_id')
    set_number = data.get('set_number')
    weight = data.get('weight')
    reps = data.get('reps')
    difficulty = data.get('difficulty', 'medium')

    # Validate
    if not all([session_id, exercise_id, set_number is not None]):
        return JsonResponse({'error': 'Missing fields'}, status=400)

    if difficulty not in ('easy', 'medium', 'hard'):
        return JsonResponse({'error': 'Invalid difficulty'}, status=400)

    try:
        weight = Decimal(str(weight))
        reps = int(reps)
        set_number = int(set_number)
    except (InvalidOperation, ValueError, TypeError):
        return JsonResponse({'error': 'Invalid numeric values'}, status=400)

    if weight < 0 or reps < 0 or set_number < 1 or set_number > 10:
        return JsonResponse({'error': 'Values out of range'}, status=400)

    # Verify session belongs to user
    session = get_object_or_404(WorkoutSession, pk=session_id, user=request.user)
    exercise = get_object_or_404(ExerciseTemplate, pk=exercise_id)

    log, created = ExerciseLog.objects.update_or_create(
        session=session,
        exercise_template=exercise,
        set_number=set_number,
        defaults={
            'weight': weight,
            'reps': reps,
            'difficulty': difficulty,
        }
    )

    return JsonResponse({
        'ok': True,
        'created': created,
        'log_id': log.pk,
    })


# ---------------------------------------------------------------------------
# API: Complete workout session
# ---------------------------------------------------------------------------

@login_required
@require_POST
def complete_session(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    session_id = data.get('session_id')
    session = get_object_or_404(WorkoutSession, pk=session_id, user=request.user)
    session.completed_at = timezone.now()
    session.save()
    return JsonResponse({'ok': True})


# ---------------------------------------------------------------------------
# Dashboard view
# ---------------------------------------------------------------------------

@login_required
@ensure_csrf_cookie
def dashboard_view(request):
    user = request.user

    # Body weight history (last 90 days)
    weight_logs = list(
        BodyWeightLog.objects
        .filter(user=user)
        .order_by('date')
        .values('date', 'weight')[:90]
    )
    weight_data = [
        {'date': w['date'].isoformat(), 'weight': float(w['weight'])}
        for w in weight_logs
    ]

    # Latest weight
    latest_weight = BodyWeightLog.objects.filter(user=user).order_by('-date').first()

    # Profile
    profile, _ = UserProfile.objects.get_or_create(user=user)

    # Session count
    total_sessions = WorkoutSession.objects.filter(
        user=user, completed_at__isnull=False
    ).count()

    # Sessions this week
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    sessions_this_week = WorkoutSession.objects.filter(
        user=user, date__gte=week_start, completed_at__isnull=False
    ).count()

    # Exercise progression data — top exercises by log count
    exercise_progress = {}
    top_exercises = (
        ExerciseLog.objects
        .filter(session__user=user)
        .values('exercise_template__id', 'exercise_template__name')
        .annotate(max_weight=Max('weight'))
        .order_by('-max_weight')[:8]
    )
    for ex in top_exercises:
        ex_id = ex['exercise_template__id']
        logs = (
            ExerciseLog.objects
            .filter(session__user=user, exercise_template_id=ex_id, set_number=1)
            .order_by('session__date')
            .values('session__date', 'weight')[:30]
        )
        exercise_progress[ex['exercise_template__name']] = [
            {'date': l['session__date'].isoformat(), 'weight': float(l['weight'])}
            for l in logs
        ]

    # Streak calculation
    streak = 0
    check_date = today
    while True:
        if check_date.weekday() >= 5:  # skip weekends
            check_date -= timedelta(days=1)
            continue
        has_session = WorkoutSession.objects.filter(
            user=user, date=check_date, completed_at__isnull=False
        ).exists()
        if has_session:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break

    context = {
        'weight_data': json.dumps(weight_data),
        'latest_weight': latest_weight,
        'target_weight': profile.target_weight,
        'total_sessions': total_sessions,
        'sessions_this_week': sessions_this_week,
        'exercise_progress': json.dumps(exercise_progress),
        'streak': streak,
        'profile': profile,
    }
    return render(request, 'workouts/dashboard.html', context)


# ---------------------------------------------------------------------------
# API: Log body weight
# ---------------------------------------------------------------------------

@login_required
@require_POST
def log_body_weight(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    try:
        weight = Decimal(str(data.get('weight', 0)))
    except (InvalidOperation, TypeError):
        return JsonResponse({'error': 'Invalid weight'}, status=400)

    if weight < 20 or weight > 300:
        return JsonResponse({'error': 'Weight out of range (20-300 kg)'}, status=400)

    log_date = data.get('date', date.today().isoformat())
    try:
        log_date = date.fromisoformat(log_date)
    except ValueError:
        log_date = date.today()

    log, created = BodyWeightLog.objects.update_or_create(
        user=request.user,
        date=log_date,
        defaults={'weight': weight}
    )

    return JsonResponse({
        'ok': True,
        'created': created,
        'weight': float(log.weight),
        'date': log.date.isoformat(),
    })


# ---------------------------------------------------------------------------
# API: Update profile
# ---------------------------------------------------------------------------

@login_required
@require_POST
def update_profile(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    height = data.get('height_cm')
    target = data.get('target_weight')

    if height is not None:
        try:
            height = int(height)
            if 100 <= height <= 250:
                profile.height_cm = height
        except (ValueError, TypeError):
            pass

    if target is not None:
        try:
            target = Decimal(str(target))
            if 30 <= target <= 250:
                profile.target_weight = target
        except (InvalidOperation, TypeError):
            pass

    profile.save()
    return JsonResponse({'ok': True})


# ---------------------------------------------------------------------------
# API: Get exercise history for charts
# ---------------------------------------------------------------------------

@login_required
@require_GET
def exercise_history(request, exercise_id):
    exercise = get_object_or_404(ExerciseTemplate, pk=exercise_id)

    try:
        days = int(request.GET.get('days', 0))
    except (ValueError, TypeError):
        days = 0

    qs = ExerciseLog.objects.filter(
        session__user=request.user, exercise_template=exercise
    )
    if days > 0:
        from_date = date.today() - timedelta(days=days)
        qs = qs.filter(session__date__gte=from_date)

    logs = (
        qs
        .order_by('session__date', 'set_number')
        .select_related('session')
        .values('session__date', 'set_number', 'weight', 'reps', 'difficulty')
    )
    data = [
        {
            'date': l['session__date'].isoformat(),
            'set': l['set_number'],
            'weight': float(l['weight']),
            'reps': l['reps'],
            'difficulty': l['difficulty'],
        }
        for l in logs
    ]
    return JsonResponse({'exercise': exercise.name, 'history': data})


# ---------------------------------------------------------------------------
# Exercise progression page
# ---------------------------------------------------------------------------

@login_required
@ensure_csrf_cookie
def exercise_progress_view(request):
    user = request.user

    logged_ids = (
        ExerciseLog.objects
        .filter(session__user=user)
        .values_list('exercise_template_id', flat=True)
        .distinct()
    )

    exercises = (
        ExerciseTemplate.objects
        .filter(id__in=logged_ids)
        .select_related('workout_plan')
        .order_by('workout_plan__display_order', 'display_order')
    )

    plans = {}
    for ex in exercises:
        plan_name = ex.workout_plan.name if ex.workout_plan else 'Other'
        if plan_name not in plans:
            plans[plan_name] = []
        plans[plan_name].append({'id': ex.id, 'name': ex.name})

    return render(request, 'workouts/exercises.html', {'plans': plans})

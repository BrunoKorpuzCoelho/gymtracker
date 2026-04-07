from django.contrib import admin
from .models import (
    WorkoutPlan, ExerciseTemplate, WorkoutSession,
    ExerciseLog, BodyWeightLog, UserProfile,
)


class ExerciseTemplateInline(admin.TabularInline):
    model = ExerciseTemplate
    extra = 1
    ordering = ['display_order']


@admin.register(WorkoutPlan)
class WorkoutPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'day_of_week', 'color', 'display_order']
    ordering = ['display_order']
    inlines = [ExerciseTemplateInline]


@admin.register(ExerciseTemplate)
class ExerciseTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'workout_plan', 'target_muscle', 'sets_reps', 'display_order']
    list_filter = ['workout_plan']
    ordering = ['workout_plan', 'display_order']


@admin.register(WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'workout_plan', 'date', 'completed_at']
    list_filter = ['user', 'workout_plan', 'date']


@admin.register(ExerciseLog)
class ExerciseLogAdmin(admin.ModelAdmin):
    list_display = ['session', 'exercise_template', 'set_number', 'weight', 'reps', 'difficulty']
    list_filter = ['difficulty']


@admin.register(BodyWeightLog)
class BodyWeightLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'weight']
    list_filter = ['user']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'height_cm', 'target_weight']

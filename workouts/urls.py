from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Pages
    path('', views.calendar_view, name='calendar'),
    path('workout/<int:plan_id>/', views.workout_view, name='workout'),
    path('workout/<int:plan_id>/<str:session_date>/', views.workout_view, name='workout_date'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('exercises/', views.exercise_progress_view, name='exercise_progress'),

    # API endpoints
    path('api/log-set/', views.save_exercise_log, name='api_log_set'),
    path('api/complete-session/', views.complete_session, name='api_complete_session'),
    path('api/log-weight/', views.log_body_weight, name='api_log_weight'),
    path('api/update-profile/', views.update_profile, name='api_update_profile'),
    path('api/exercise-history/<int:exercise_id>/', views.exercise_history, name='api_exercise_history'),
]

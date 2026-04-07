from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class WorkoutPlan(models.Model):
    """A workout template for a given day (e.g. 'Back + Biceps')."""

    DAYS = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
    ]

    name = models.CharField(max_length=100)
    day_of_week = models.IntegerField(choices=DAYS, null=True, blank=True)
    color = models.CharField(max_length=7, default='#457B9D')  # hex
    tag = models.CharField(max_length=100, blank=True, default='')
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        day_label = dict(self.DAYS).get(self.day_of_week, 'Any')
        return f"{day_label} — {self.name}"


class ExerciseTemplate(models.Model):
    """An exercise within a workout plan template."""

    workout_plan = models.ForeignKey(
        WorkoutPlan, on_delete=models.CASCADE, related_name='exercises'
    )
    name = models.CharField(max_length=150)
    target_muscle = models.CharField(max_length=100)
    category = models.CharField(max_length=50, blank=True, default='')
    sets_reps = models.CharField(
        max_length=30, default='12 / 10 / 8',
        help_text='Rep scheme per set, e.g. "12 / 10 / 8" or "max / max / max"'
    )
    tip = models.TextField(blank=True, default='')
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return f"{self.name} ({self.workout_plan.name})"

    @property
    def planned_sets(self):
        """Return list of target reps, e.g. [12, 10, 8]."""
        parts = [p.strip() for p in self.sets_reps.split('/')]
        result = []
        for p in parts:
            try:
                result.append(int(p))
            except ValueError:
                result.append(0)  # 0 = to failure
        return result


class WorkoutSession(models.Model):
    """A recorded workout on a specific date."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='workout_sessions'
    )
    workout_plan = models.ForeignKey(
        WorkoutPlan, on_delete=models.SET_NULL, null=True,
        related_name='sessions'
    )
    date = models.DateField()
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-date']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'workout_plan', 'date'],
                name='unique_session_per_plan_per_day'
            )
        ]

    def __str__(self):
        plan_name = self.workout_plan.name if self.workout_plan else 'Custom'
        return f"{self.user.username} — {plan_name} — {self.date}"


class ExerciseLog(models.Model):
    """Logged performance for a single set of a single exercise."""

    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    session = models.ForeignKey(
        WorkoutSession, on_delete=models.CASCADE, related_name='exercise_logs'
    )
    exercise_template = models.ForeignKey(
        ExerciseTemplate, on_delete=models.SET_NULL, null=True,
        related_name='logs'
    )
    set_number = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    weight = models.DecimalField(
        max_digits=6, decimal_places=1, default=0,
        validators=[MinValueValidator(0)]
    )
    reps = models.PositiveIntegerField(default=0)
    difficulty = models.CharField(
        max_length=6, choices=DIFFICULTY_CHOICES, default='medium'
    )

    class Meta:
        ordering = ['exercise_template__display_order', 'set_number']
        constraints = [
            models.UniqueConstraint(
                fields=['session', 'exercise_template', 'set_number'],
                name='unique_set_per_exercise_per_session'
            )
        ]

    def __str__(self):
        ex_name = self.exercise_template.name if self.exercise_template else '?'
        return f"{ex_name} — Set {self.set_number}: {self.weight}kg x {self.reps}"


class BodyWeightLog(models.Model):
    """Daily body weight tracking."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='weight_logs'
    )
    date = models.DateField()
    weight = models.DecimalField(
        max_digits=5, decimal_places=1,
        validators=[MinValueValidator(20), MaxValueValidator(300)]
    )

    class Meta:
        ordering = ['-date']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'date'],
                name='unique_weight_per_day'
            )
        ]

    def __str__(self):
        return f"{self.user.username} — {self.date}: {self.weight}kg"


class UserProfile(models.Model):
    """Extended user info for fitness tracking."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='profile'
    )
    height_cm = models.PositiveIntegerField(null=True, blank=True)
    target_weight = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True
    )

    def __str__(self):
        return f"Profile: {self.user.username}"

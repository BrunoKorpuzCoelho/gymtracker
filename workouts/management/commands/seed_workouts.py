from django.core.management.base import BaseCommand
from workouts.models import WorkoutPlan, ExerciseTemplate

_B = 'https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises'


def _imgs(exercise_id):
    return f'{_B}/{exercise_id}/0.jpg,{_B}/{exercise_id}/1.jpg'


PLANS = [
    {
        'name': 'Back + Biceps',
        'day_of_week': 0,  # Monday
        'color': '#457B9D',
        'tag': '🏀 Basketball night',
        'order': 0,
        'exercises': [
            {'name': 'Lat Pulldown (wide grip)', 'target': 'Lats (width)', 'cat': '', 'sets': '12 / 10 / 8', 'tip': 'Wide grip. Pull to chest, never behind the neck.', 'order': 0, 'demo': _imgs('Wide-Grip_Lat_Pulldown')},
            {'name': 'Barbell Bent-Over Row', 'target': 'Back (thickness)', 'cat': '', 'sets': '12 / 10 / 8', 'tip': 'Keep back straight, pull to belly button. King of back exercises.', 'order': 1, 'demo': _imgs('Bent_Over_Barbell_Row')},
            {'name': 'Single-Arm Dumbbell Row', 'target': 'Lats', 'cat': '', 'sets': '12 / 10 / 8', 'tip': 'One arm at a time. Feel the lat stretch and contract.', 'order': 2, 'demo': _imgs('One-Arm_Dumbbell_Row')},
            {'name': 'Seated Cable Row', 'target': 'Back (general)', 'cat': '', 'sets': '12 / 10 / 8', 'tip': 'Neutral grip. Chest out on contraction, don\'t swing your torso.', 'order': 3, 'demo': _imgs('Seated_Cable_Rows_-_Cable_Attachment')},
            {'name': 'EZ Bar Curl', 'target': 'Biceps', 'cat': '', 'sets': '12 / 10 / 8', 'tip': 'Elbows pinned to sides. No swinging — if you need to swing, lower the weight.', 'order': 4, 'demo': _imgs('EZ-Bar_Curl')},
            {'name': 'Alternating Dumbbell Curl', 'target': 'Biceps', 'cat': '', 'sets': '12 / 10 / 8', 'tip': 'Rotate wrist at the top (supination) for maximum activation.', 'order': 5, 'demo': _imgs('Dumbbell_Alternate_Bicep_Curl')},
            {'name': 'Hammer Curl', 'target': 'Brachialis + forearm', 'cat': '', 'sets': '12 / 10 / 8', 'tip': 'Neutral grip. Builds arm thickness — it\'s not just about biceps.', 'order': 6, 'demo': _imgs('Hammer_Curls')},
        ],
    },
    {
        'name': 'Chest + Triceps',
        'day_of_week': 1,  # Tuesday
        'color': '#E63946',
        'tag': '',
        'order': 1,
        'exercises': [
            {'name': 'Barbell Bench Press', 'target': 'Chest (general)', 'cat': '', 'sets': '12 / 10 / 8', 'tip': 'Foundation of chest training. Control the descent (2-3s). Ask for a spot on last reps.', 'order': 0, 'demo': _imgs('Barbell_Bench_Press_-_Medium_Grip')},
            {'name': 'Incline Dumbbell Press', 'target': 'Upper chest', 'cat': '', 'sets': '12 / 10 / 8', 'tip': 'Bench at 30-45°. Open wide on the way down to stretch.', 'order': 1, 'demo': _imgs('Incline_Dumbbell_Press')},
            {'name': 'Cable Crossover (or Flyes)', 'target': 'Chest (definition)', 'cat': '', 'sets': '12 / 10 / 8', 'tip': 'Focus on contraction. Slightly cross hands at the end.', 'order': 2, 'demo': _imgs('Low_Cable_Crossover')},
            {'name': 'Chest Press Machine', 'target': 'Chest (general)', 'cat': '', 'sets': '12 / 10 / 8', 'tip': 'Great for finishing without injury risk.', 'order': 3, 'demo': _imgs('Leverage_Chest_Press')},
            {'name': 'Triceps Pushdown (rope)', 'target': 'Triceps', 'cat': '', 'sets': '12 / 10 / 8', 'tip': 'Spread the rope at the bottom to activate the lateral head.', 'order': 4, 'demo': _imgs('Triceps_Pushdown')},
            {'name': 'Overhead Triceps Extension (EZ bar)', 'target': 'Triceps (long head)', 'cat': '', 'sets': '12 / 10 / 8', 'tip': 'Elbows point up, keep them steady. Lower behind head.', 'order': 5, 'demo': _imgs('EZ_Bar_Overhead_Tricep_Extension')},
            {'name': 'Bench Dips', 'target': 'Triceps', 'cat': '', 'sets': '12 / 10 / 8', 'tip': 'Feet on floor (beginner) or elevated. Add weight when comfortable.', 'order': 6, 'demo': _imgs('Bench_Dips')},
        ],
    },
    {
        'name': 'Legs + Shoulders + Traps',
        'day_of_week': 2,  # Wednesday
        'color': '#2A9D8F',
        'tag': '💪 Full day',
        'order': 2,
        'exercises': [
            {'name': 'Barbell Squat', 'target': 'Quads + glutes', 'cat': 'LEGS', 'sets': '12 / 10 / 8', 'tip': 'King of exercises. Go to parallel. Start light and build up.', 'order': 0, 'demo': _imgs('Barbell_Squat')},
            {'name': 'Leg Press 45°', 'target': 'Quads + glutes', 'cat': 'LEGS', 'sets': '12 / 10 / 8', 'tip': 'Feet higher = more glutes. Feet lower = more quads.', 'order': 1, 'demo': _imgs('Leg_Press')},
            {'name': 'Leg Extension', 'target': 'Quads (isolation)', 'cat': 'LEGS', 'sets': '12 / 10 / 8', 'tip': 'Squeeze at the top for 1-2 seconds. Great for definition.', 'order': 2, 'demo': _imgs('Leg_Extensions')},
            {'name': 'Lying Leg Curl', 'target': 'Hamstrings', 'cat': 'LEGS', 'sets': '12 / 10 / 8', 'tip': 'Don\'t let the weight slam. Control the eccentric (return).', 'order': 3, 'demo': _imgs('Lying_Leg_Curls')},
            {'name': 'Standing Calf Raise', 'target': 'Calves', 'cat': 'LEGS', 'sets': '15 / 12 / 10', 'tip': 'Calves need more reps. Pause at the bottom 2s, explode up.', 'order': 4, 'demo': _imgs('Standing_Calf_Raises')},
            {'name': 'Seated Dumbbell Press', 'target': 'Front + lateral delts', 'cat': 'SHOULDERS', 'sets': '12 / 10 / 8', 'tip': 'Bench at 90°. Push up without locking elbows at the top.', 'order': 5, 'demo': _imgs('Seated_Dumbbell_Press')},
            {'name': 'Lateral Raises', 'target': 'Lateral delt (width)', 'cat': 'SHOULDERS', 'sets': '12 / 10 / 8', 'tip': 'Light weight, perfect form. Slight elbow bend, raise to shoulder level.', 'order': 6, 'demo': _imgs('Side_Lateral_Raise')},
            {'name': 'Face Pull (high cable)', 'target': 'Rear delt + posture', 'cat': 'SHOULDERS', 'sets': '12 / 10 / 8', 'tip': 'Essential for shoulder health and posture. Never skip this.', 'order': 7, 'demo': _imgs('Face_Pull')},
            {'name': 'Alternating Front Raises', 'target': 'Front delt', 'cat': 'SHOULDERS', 'sets': '12 / 10 / 8', 'tip': 'Raise to eye level, no higher. Alternate arms.', 'order': 8, 'demo': _imgs('Front_Dumbbell_Raise')},
            {'name': 'Dumbbell Shrugs', 'target': 'Traps', 'cat': 'TRAPS', 'sets': '12 / 10 / 8', 'tip': 'Shoulders to ears. No rolling — straight up and down. Go heavy here.', 'order': 9, 'demo': _imgs('Dumbbell_Shrug')},
        ],
    },
    {
        'name': 'Back + Biceps',
        'day_of_week': 3,  # Thursday
        'color': '#457B9D',
        'tag': '🏀 Basketball night',
        'order': 3,
        'exercises': [
            {'name': 'Close-Grip Lat Pulldown', 'target': 'Lats (thickness)', 'cat': '', 'sets': '12 / 10 / 8', 'tip': 'Close neutral grip — different stimulus from Monday\'s wide grip.', 'order': 0, 'demo': _imgs('Close-Grip_Lat_Pulldown')},
            {'name': 'Dumbbell Bent-Over Row', 'target': 'Back (thickness)', 'cat': '', 'sets': '12 / 10 / 8', 'tip': 'Dumbbells instead of barbell. More range of motion.', 'order': 1, 'demo': _imgs('Bent_Over_Two-Dumbbell_Row')},
            {'name': 'Pullover (dumbbell or machine)', 'target': 'Lats + serratus', 'cat': '', 'sets': '12 / 10 / 8', 'tip': 'Arms nearly straight, feel the lat stretch. Different angle.', 'order': 2, 'demo': _imgs('Straight-Arm_Dumbbell_Pullover')},
            {'name': 'Seated Cable Row (wide grip)', 'target': 'Back (width)', 'cat': '', 'sets': '12 / 10 / 8', 'tip': 'Wide grip for more mid-traps and rhomboids.', 'order': 3, 'demo': _imgs('Seated_Cable_Rows_-_Cable_Attachment')},
            {'name': 'Incline Dumbbell Curl', 'target': 'Biceps (long head)', 'cat': '', 'sets': '12 / 10 / 8', 'tip': 'Bench at 45°. Arms hang back — greater bicep stretch.', 'order': 4, 'demo': _imgs('Alternate_Incline_Dumbbell_Curl')},
            {'name': 'Concentration Curl', 'target': 'Biceps (peak)', 'cat': '', 'sets': '12 / 10 / 8', 'tip': 'Seated, elbow on thigh. Fully isolates the bicep.', 'order': 5, 'demo': _imgs('Concentration_Curl')},
        ],
    },
    {
        'name': 'Chest + Triceps',
        'day_of_week': 4,  # Friday
        'color': '#E63946',
        'tag': '🔥 Close the week',
        'order': 4,
        'exercises': [
            {'name': 'Incline Barbell Press', 'target': 'Upper chest', 'cat': '', 'sets': '12 / 10 / 8', 'tip': 'Start with incline on Friday — variation from Tuesday\'s flat start.', 'order': 0, 'demo': _imgs('Barbell_Incline_Bench_Press_-_Medium_Grip')},
            {'name': 'Flat Dumbbell Press', 'target': 'Chest (general)', 'cat': '', 'sets': '12 / 10 / 8', 'tip': 'Dumbbells instead of barbell — more range and stabilization.', 'order': 1, 'demo': _imgs('Dumbbell_Bench_Press')},
            {'name': 'Pec Deck (Butterfly)', 'target': 'Chest (contraction)', 'cat': '', 'sets': '12 / 10 / 8', 'tip': 'Squeeze 1-2s at the end of each rep.', 'order': 2, 'demo': _imgs('Pec_Deck_Fly')},
            {'name': 'Push-ups (to failure)', 'target': 'Chest + triceps', 'cat': '', 'sets': 'max / max / max', 'tip': 'Last chest exercise — go to failure. No ego, perfect form.', 'order': 3, 'demo': _imgs('Pushups')},
            {'name': 'Triceps Pushdown (straight bar)', 'target': 'Triceps (lateral)', 'cat': '', 'sets': '12 / 10 / 8', 'tip': 'Straight bar instead of rope — different stimulus from Tuesday.', 'order': 4, 'demo': _imgs('Triceps_Pushdown')},
            {'name': 'Skull Crushers (EZ bar)', 'target': 'Triceps (long head)', 'cat': '', 'sets': '12 / 10 / 8', 'tip': 'EZ bar. Lower to forehead, keep elbows steady. Watch the weight.', 'order': 5, 'demo': _imgs('Skull_Crusher')},
            {'name': 'Dumbbell Kickback', 'target': 'Triceps', 'cat': '', 'sets': '12 / 10 / 8', 'tip': 'Light weight, max squeeze at the top. Good finisher.', 'order': 6, 'demo': _imgs('Tricep_Dumbbell_Kickback')},
        ],
    },
]


class Command(BaseCommand):
    help = 'Seed workout plans and exercises'

    def handle(self, *args, **options):
        for plan_data in PLANS:
            plan, created = WorkoutPlan.objects.update_or_create(
                name=plan_data['name'],
                day_of_week=plan_data['day_of_week'],
                defaults={
                    'color': plan_data['color'],
                    'tag': plan_data['tag'],
                    'display_order': plan_data['order'],
                }
            )
            action = 'Created' if created else 'Updated'
            self.stdout.write(f"  {action} plan: {plan}")

            for ex_data in plan_data['exercises']:
                ex, ex_created = ExerciseTemplate.objects.update_or_create(
                    workout_plan=plan,
                    name=ex_data['name'],
                    defaults={
                        'target_muscle': ex_data['target'],
                        'category': ex_data['cat'],
                        'sets_reps': ex_data['sets'],
                        'tip': ex_data['tip'],
                        'demo_url': ex_data.get('demo', ''),
                        'display_order': ex_data['order'],
                    }
                )
                ex_action = 'Created' if ex_created else 'Updated'
                self.stdout.write(f"    {ex_action} exercise: {ex.name}")

        self.stdout.write(self.style.SUCCESS('\nDone! All workout plans seeded.'))

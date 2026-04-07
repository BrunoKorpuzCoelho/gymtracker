# GymTracker 🏋️

Personal gym workout tracker built with Django + PostgreSQL. Track your workouts, log weights and reps, get progressive overload suggestions, and monitor your progress over time.

## Features

- **Smart Calendar** — Auto-detects today's workout (Mon-Fri). Pick any workout on weekends.
- **Exercise Logging** — Log weight, reps, and difficulty for every set of every exercise.
- **Progressive Overload** — Automatic suggestions to increase weight based on previous difficulty ratings.
- **Body Weight Tracking** — Log daily weight with chart visualization.
- **Strength Progress Charts** — Track weight lifted per exercise over time.
- **Streak Counter** — See your consecutive training days.
- **Mobile-First Dark UI** — Designed for 6 AM gym sessions on your phone.
- **Production Security** — CSRF protection, session security, input sanitization, XSS prevention, SQL injection protection (Django ORM), HTTPS hardening.

## Tech Stack

- **Backend**: Django 5.1+, PostgreSQL
- **Frontend**: Vanilla HTML/CSS/JS (no frameworks)
- **Security**: Django's built-in CSRF, session management, password hashing, input sanitization (bleach)

---

## Quick Start (Development)

### 1. Prerequisites
- Python 3.11+
- PostgreSQL 14+

### 2. Create the database

```bash
sudo -u postgres psql
CREATE DATABASE gymtracker;
CREATE USER gymtracker WITH PASSWORD 'gymtracker';
ALTER ROLE gymtracker SET client_encoding TO 'utf8';
ALTER ROLE gymtracker SET default_transaction_isolation TO 'read committed';
ALTER ROLE gymtracker SET timezone TO 'Europe/Lisbon';
GRANT ALL PRIVILEGES ON DATABASE gymtracker TO gymtracker;
\q
```

### 3. Setup the project

```bash
cd gymtracker
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 4. Run migrations & seed data

```bash
python manage.py migrate
python manage.py seed_workouts
python manage.py createsuperuser
```

### 5. Run the dev server

```bash
python manage.py runserver
```

Open http://localhost:8000 — register an account and start tracking.

---

## Production Deployment (Contabo VPS)

### 1. Clone & setup

```bash
cd /opt
git clone <your-repo-url> gymtracker
cd gymtracker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment variables

```bash
cp .env.example .env
nano .env  # fill in production values
```

Generate a secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Database (production)

```bash
sudo -u postgres psql
CREATE DATABASE gymtracker;
CREATE USER gymtracker WITH PASSWORD '<STRONG_PASSWORD>';
GRANT ALL PRIVILEGES ON DATABASE gymtracker TO gymtracker;
\q
```

### 4. Migrate & collect static

```bash
source venv/bin/activate
python manage.py migrate
python manage.py seed_workouts
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 5. Gunicorn systemd service

Create `/etc/systemd/system/gymtracker.service`:

```ini
[Unit]
Description=GymTracker Django App
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/gymtracker
EnvironmentFile=/opt/gymtracker/.env
ExecStart=/opt/gymtracker/venv/bin/gunicorn gymtracker.wsgi:application \
    --bind 127.0.0.1:8001 \
    --workers 2 \
    --timeout 120
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable gymtracker
sudo systemctl start gymtracker
```

### 6. Nginx config

```nginx
server {
    listen 80;
    server_name gym.yourdomain.com;

    location /static/ {
        alias /opt/gymtracker/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Then setup SSL with Certbot:
```bash
sudo certbot --nginx -d gym.yourdomain.com
```

---

## Security Checklist

- [x] CSRF tokens on all forms and AJAX requests
- [x] Session cookies: HttpOnly, SameSite=Lax
- [x] Input sanitization with bleach (all text inputs)
- [x] Django ORM prevents SQL injection
- [x] Django templates auto-escape prevents XSS
- [x] Password validation (min 8 chars, not common, not numeric)
- [x] `json_script` template tag for safe JSON embedding
- [x] All API endpoints require authentication
- [x] All write endpoints require POST
- [x] Ownership verification on all data mutations
- [x] Production: HTTPS redirect, HSTS, secure cookies, X-Frame-Options DENY

---

## Workout Split

| Day       | Workout                     | Note              |
|-----------|-----------------------------|--------------------|
| Monday    | Back + Biceps               | Basketball at night |
| Tuesday   | Chest + Triceps             |                    |
| Wednesday | Legs + Shoulders + Traps    | Full day           |
| Thursday  | Back + Biceps (variations)  | Basketball at night |
| Friday    | Chest + Triceps (variations)|                    |

---

## Management Commands

```bash
python manage.py seed_workouts    # Populate workout plans & exercises
python manage.py createsuperuser  # Create admin user
```

Access Django admin at `/admin/` to edit workout plans, exercises, and view all data.

## Job Portal (Django)

A full‑stack Django application for posting jobs and tracking applications. It includes user registration/login with email verification, password reset, job advert creation, application tracking, and asynchronous email notifications via Celery and Redis.

### Features

- **Accounts**: Registration, login, email verification, password reset
- **Jobs**: Create, list, and manage job adverts
- **Applications**: Apply to jobs, view your applications, employer views of applicants
- **Async Emails**: Celery tasks with Redis broker

### Tech Stack

- **Backend**: Django 5
- **Task Queue**: Celery + Redis
- **DB**: SQLite (dev default)
- **Testing**: pytest + pytest‑django + factory_boy

---

## Quick Start

### 1) Clone and enter the project

```bash
git clone https://github.com/mhrznIndrik/JOB_PORTAL.git
cd JOB_PORTAL
```

### 2) Create a virtual environment (optional if you use the bundled venv)

```bash
python -m venv .venv
source .venv/bin/activate    # Windows (Git Bash): source venv/Scripts/activate or .venv/Scripts/activate
```

If you prefer the bundled `venv`, activate it:

```bash
source venv/Scripts/activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Configure environment variables

Create a `.env` file at the project root with the following keys:

```dotenv
SECRET_KEY=change-me

# SMTP (example uses Gmail SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_app_password

# Optional: override defaults
# DEBUG=True
# CELERY_BROKER_URL=redis://localhost:6379
# CELERY_RESULT_BACKEND=redis://localhost:6379
```

Environment variables are read via `python-decouple` in `job_portal/settings.py`.

### 5) Apply migrations

```bash
python manage.py migrate
```

### 6) Start Redis (required for Celery)

- Install Redis and run it locally. On Windows, use WSL/Docker or a native port.
- Default URL is `redis://localhost:6379`.

### 7) Run the app and workers

In one terminal:

```bash
python manage.py runserver
```

In another terminal (with venv activated):

```bash
celery -A job_portal worker -l info
```

Optional: start a beat scheduler if you add periodic tasks later:

```bash
celery -A job_portal beat -l info
```

Visit the site at `http://127.0.0.1:8000/`.

---

## Running Tests

```bash
pytest -q
```

Tests live under `accounts/tests/` and `application_tracking/tests/` and use factories in each app.

---

## Project Structure (high level)

```
JOB_PORTAL/
├─ accounts/                 # Auth, registration, email verification, password reset
├─ application_tracking/     # Job adverts and applications
├─ common/                   # Shared models/tasks
├─ job_portal/               # Project settings, URLs, Celery app, static
├─ templates/                # Base templates and email templates
├─ media/                    # Uploaded files (e.g., CVs)
└─ requirements.txt
```

Key settings are in `job_portal/settings.py`. Celery app is initialized in `job_portal/celery.py`.

---

## Environment & Configuration

- **SECRET_KEY**: required. Loaded from `.env`.
- **Email SMTP**: configure `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` for verification and password reset emails.
- **Celery/Redis**: defaults to `redis://localhost:6379` for both broker and backend. Override with `.env` if needed.
- **Static/Media**: static served from `job_portal/static` in dev; uploads stored under `media/`.

---

## Common Commands

```bash
# Run dev server
python manage.py runserver

# Make/apply migrations
python manage.py makemigrations
python manage.py migrate

# Collect static (for production)
python manage.py collectstatic

# Start Celery worker
celery -A job_portal worker -l info
```

---

## Notes for Production

- Set `DEBUG=False`, configure `ALLOWED_HOSTS`, and a strong `SECRET_KEY`.
- Use a production DB (PostgreSQL recommended) and a production‑grade email provider.
- Serve static/media via a proper web server or object storage (e.g., S3).
- Run Celery workers and Redis as managed services or containers.

---

## License

This project is licensed under the terms of the MIT License. See `LICENSE`.

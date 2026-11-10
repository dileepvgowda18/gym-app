# 🏋️ IronCore Gym – Gym Management System

## 1.Project Introduction

IronCore Gym is a full-stack gym management application for handling member accounts, membership plans, trainers, classes, bookings, simulated payments, attendance, workout logs, and trainer appointments.

The application combines a React and Vite frontend with a Flask REST API, SQLAlchemy ORM, and PostgreSQL database.

**Repository:** [dileepvgowda18/gym-app](https://github.com/dileepvgowda18/gym-app)

## 2. Project Features

| Area | Implemented functionality |
|---|---|
| Members | Member registration and login, member dashboard with membership, confirmed class bookings, and payment history. |
| Memberships | Browse active plans and subscribe; admins can create, edit, and deactivate plans. |
| Trainers | Browse trainer profiles; admins can create, edit, and remove trainer profiles. |
| Classes | Browse class schedules and seat availability; admins and trainers can create or edit classes. |
| Bookings | Authenticated users can book classes subject to capacity and duplicate-booking checks; owners and admins can cancel bookings. |
| Payments | Membership subscription records a payment marked completed. This is a simulated payment flow; no payment provider is integrated. |
| Attendance | Members can check in and out and view their own visit history; admin reporting endpoints provide attendance lists and summaries. |
| Workouts | Members can log workout sessions and exercises; trainers/admins can create workout plans through the API. |
| Appointments | Members can check availability and request trainer appointments; trainers/admins can review and update appointments through the API. |
| Administration | Admin UI for overview statistics, member search/filter, and plan, trainer, and class management. |

### 5. Member Dashboard

The `/dashboard` page shows the signed-in user's active membership, confirmed class bookings, and payment history. Members can cancel a booking there. Separate member pages support attendance check-in/out, workout logging, and trainer appointment requests.

### 6. Admin Dashboard

The `/admin` page includes overview metrics for members, active memberships, recorded revenue, confirmed bookings, and classes. Admins can search and filter members and manage plans, trainer profiles, and classes.

Attendance, workout, and appointment summaries are exposed through admin API routes; they are not dashboard panels in the current frontend.

### 7. Trainer Dashboard

The frontend does **not** have a dedicated trainer dashboard. Trainers can access backend API operations for creating/editing classes, viewing and managing their assigned appointments, and creating/viewing workout plans. The frontend's shared `/dashboard` route displays the member-oriented dashboard for trainers as well.

## 3. Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React 19, Vite 8, JavaScript, CSS, React Router, Axios |
| Backend | Python, Flask 3, Flask-SQLAlchemy, SQLAlchemy, Flask-Migrate |
| Authentication | Flask-JWT-Extended |
| Database | PostgreSQL, psycopg2 |
| Supporting packages | Flask-CORS, python-dotenv, Werkzeug, Marshmallow |
| Development tools | Git, GitHub, VS Code |

Backend package versions are pinned in [`backend/requirements.txt`](backend/requirements.txt). Frontend dependencies and scripts are listed in [`frontend/package.json`](frontend/package.json) and locked in `frontend/package-lock.json`. The repository does not pin PostgreSQL or Git versions.

## 4. System Architecture

```mermaid
flowchart TD
    Browser[React and Vite frontend] -->|HTTP and JSON| API[Flask REST API]
    Browser -->|Bearer token on protected requests| JWT[JWT authentication]
    API --> Roles[Role and ownership checks]
    API --> ORM[SQLAlchemy ORM]
    ORM --> DB[(PostgreSQL)]
```

The frontend calls the Flask API at `http://localhost:5000/api` by default. Flask routes enforce authentication and role checks, then use SQLAlchemy models to access PostgreSQL. Cross-origin API requests are configured through the backend `CORS_ORIGINS` setting.

## 8. PostgreSQL Database Design

Flask-SQLAlchemy defines the application's relational schema. Foreign keys connect member accounts, plans, trainers, classes, bookings, attendance, workouts, payments, and appointments. Detailed tables and associations are listed below.

## 9. Database Tables and Relationships

| Table | Primary key | Foreign keys and purpose |
|---|---|---|
| `users` | `id` | Member, trainer-login, and admin accounts; email is unique; stores a password hash. |
| `trainers` | `id` | `user_id` → `users.id`; trainer profile information. |
| `plans` | `id` | Membership plan price, duration, features, and active state. |
| `memberships` | `id` | `user_id` → `users.id`; `plan_id` → `plans.id`; membership dates and status. |
| `payments` | `id` | `user_id` → `users.id`; nullable `membership_id` → `memberships.id`; payment record and unique nullable transaction ID. |
| `classes` | `id` | `trainer_id` → `trainers.id`; class schedule and capacity. |
| `bookings` | `id` | `user_id` → `users.id`; `class_id` → `classes.id`; reservation and status. |
| `attendance` | `attendance_id` | `member_id` → `users.id`; check-in/check-out timestamps and indexes. |
| `exercises` | `exercise_id` | Exercise catalog; exercise name is unique. |
| `workout_sessions` | `session_id` | `member_id` → `users.id`; dated workout session and notes. |
| `workout_entries` | `entry_id` | `session_id` → `workout_sessions.session_id`; `exercise_id` → `exercises.exercise_id`; sets, repetitions, weight, and notes. |
| `workout_plans` | `plan_id` | `trainer_id` → `trainers.id`; `member_id` → `users.id`; trainer-authored plan assigned to a member. |
| `plan_exercises` | `id` | `plan_id` → `workout_plans.plan_id`; `exercise_id` → `exercises.exercise_id`; prescribed sets, repetitions, and target weight. |
| `trainer_appointments` | `appointment_id` | `member_id` → `users.id`; `trainer_id` → `trainers.id`; appointment times, status, and notes. |

One-to-many relationships include users to memberships, bookings, payments, attendance records, workout sessions, workout plans, and member appointments; plans to memberships; trainers to classes, workout plans, and trainer appointments; classes to bookings; workout sessions to workout entries; and workout plans to plan exercises.

There is no standalone many-to-many table. `workout_entries` links workout sessions and exercises, while `plan_exercises` links workout plans and exercises; both tables also store relationship-specific training values.

Model-level constraints include unique user email, unique exercise name, unique nullable payment transaction ID, positive sets and repetitions, non-negative workout weights, valid appointment status, and appointment end time after start time. `trainers.user_id` is a foreign key but is not declared unique in the database.

## 10. Entity Relationship Diagram

```mermaid
erDiagram
    USERS {
        int id PK
        string name
        string email UK
        string password_hash
        string role
    }
    TRAINERS {
        int id PK
        int user_id FK
        string specialization
    }
    PLANS {
        int id PK
        string name
        decimal price
        int duration_days
        boolean is_active
    }
    MEMBERSHIPS {
        int id PK
        int user_id FK
        int plan_id FK
        date start_date
        date end_date
        string status
    }
    PAYMENTS {
        int id PK
        int user_id FK
        int membership_id FK
        decimal amount
        string transaction_id UK
        string status
    }
    CLASSES {
        int id PK
        int trainer_id FK
        string name
        string schedule_day
        string schedule_time
        int capacity
    }
    BOOKINGS {
        int id PK
        int user_id FK
        int class_id FK
        string status
    }
    ATTENDANCE {
        int attendance_id PK
        int member_id FK
        datetime check_in
        datetime check_out
    }
    EXERCISES {
        int exercise_id PK
        string exercise_name UK
        string muscle_group
    }
    WORKOUT_SESSIONS {
        int session_id PK
        int member_id FK
        date workout_date
    }
    WORKOUT_ENTRIES {
        int entry_id PK
        int session_id FK
        int exercise_id FK
        int sets
        int repetitions
        float weight_kg
    }
    WORKOUT_PLANS {
        int plan_id PK
        int trainer_id FK
        int member_id FK
        string plan_name
    }
    PLAN_EXERCISES {
        int id PK
        int plan_id FK
        int exercise_id FK
        int sets
        int repetitions
        float target_weight_kg
    }
    TRAINER_APPOINTMENTS {
        int appointment_id PK
        int member_id FK
        int trainer_id FK
        datetime start_at
        datetime end_at
        string status
    }

    USERS ||--o{ TRAINERS : has_profile
    USERS ||--o{ MEMBERSHIPS : holds
    PLANS ||--o{ MEMBERSHIPS : selected_for
    USERS ||--o{ PAYMENTS : makes
    MEMBERSHIPS o|--o{ PAYMENTS : associated_with
    TRAINERS ||--o{ CLASSES : leads
    USERS ||--o{ BOOKINGS : makes
    CLASSES ||--o{ BOOKINGS : receives
    USERS ||--o{ ATTENDANCE : records
    USERS ||--o{ WORKOUT_SESSIONS : logs
    WORKOUT_SESSIONS ||--o{ WORKOUT_ENTRIES : contains
    EXERCISES ||--o{ WORKOUT_ENTRIES : used_in
    TRAINERS ||--o{ WORKOUT_PLANS : creates
    USERS ||--o{ WORKOUT_PLANS : assigned_to
    WORKOUT_PLANS ||--o{ PLAN_EXERCISES : contains
    EXERCISES ||--o{ PLAN_EXERCISES : prescribed
    USERS ||--o{ TRAINER_APPOINTMENTS : requests
    TRAINERS ||--o{ TRAINER_APPOINTMENTS : receives
```

## 11. Project Folder Structure

```text
gym-app/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── __init__.py
│   │   ├── decorators.py
│   │   └── extensions.py
│   ├── .env.example
│   ├── config.py
│   ├── requirements.txt
│   ├── run.py
│   └── seed.py
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── api/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── context/
│   │   ├── pages/
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
├── .gitignore
└── README.md
```

## 12. Installation Requirements

| Requirement | Version or notes |
|---|---|
| Python | 3.9 or newer (the project uses `zoneinfo`). |
| Node.js | `^20.19.0` or `>=22.12.0` for the locked Vite toolchain. |
| PostgreSQL | Installed and running locally or available remotely; no version is pinned in the repository. |
| Git | Required to clone the repository. |
| Windows PowerShell | Commands below use PowerShell syntax. |

On Windows, the IANA timezone data used by Python `zoneinfo` may require the optional `tzdata` package. See [Troubleshooting](#troubleshooting).

## 13. PostgreSQL Database Setup

1. Install PostgreSQL for Windows and start its service.
2. Open `psql` or the PostgreSQL SQL Shell with permission to create a role and database.
3. Create an application role and database. Substitute a private password locally; do not put real credentials in this README.

```sql
CREATE ROLE gym_user WITH LOGIN PASSWORD 'replace-with-your-own-password';
CREATE DATABASE gym_db OWNER gym_user;
```

4. Configure `DATABASE_URL` in `backend\.env`:

```dotenv
DATABASE_URL=postgresql+psycopg2://gym_user:YOUR_PASSWORD@localhost:5432/gym_db
```

The backend normalizes `postgresql://` URLs to the installed `psycopg2` driver. URL-encode reserved characters in a password. Do not commit `.env` files.

## 14. Backend Setup (Windows PowerShell)

From the repository root, create a virtual environment and install dependencies:

```powershell
Set-Location backend
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `backend\.env` with the database URL and development secrets before running the API. If script activation is blocked in PowerShell, allow it for the current process only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### Initialize the Database

For local development, the seed script calls `db.create_all()` and inserts sample records:

```powershell
python seed.py
```

It does not print passwords in this documentation. The seed code includes static demo account credentials; use this script only with a development database and change/remove seeded accounts before deployment.

Flask-Migrate is configured, but a migrations directory is not included in the repository. To initialize migrations for the first time, run from `backend`:

```powershell
$env:FLASK_APP = "run.py"
flask db init
flask db migrate -m "Initial schema"
flask db upgrade
```

Review generated migrations before upgrading. For future model changes, create and review a new migration, then apply it with `flask db upgrade`. `db.create_all()` creates missing tables but does not update existing tables; do not drop tables to resolve migration problems.

### Start the Backend

From `backend`, with the virtual environment active:

```powershell
python run.py
```

The API listens at `http://localhost:5000`. Its health endpoint is `http://localhost:5000/api/health`.

## 15. Frontend Setup

Open a second PowerShell window at the repository root:

```powershell
Set-Location frontend
npm install
npm run dev
```

Vite serves the frontend at `http://localhost:5173` by default. The API client uses `http://localhost:5000/api` unless `VITE_API_URL` is set.

Create and preview a production build:

```powershell
npm run build
npm run preview
```

The build output is written to `frontend\dist`.

## 16. Environment Variables

| Variable | Used by | Purpose |
|---|---|---|
| `DATABASE_URL` | Backend | SQLAlchemy PostgreSQL connection URL. |
| `SECRET_KEY` | Backend | Flask application secret; set a unique random value outside development. |
| `JWT_SECRET_KEY` | Backend | JWT signing secret; set a separate unique random value. Access tokens expire after 12 hours. |
| `CORS_ORIGINS` | Backend | Comma-separated allowed frontend origins; defaults to `http://localhost:5173`. |
| `VITE_API_URL` | Frontend (optional) | API base URL; defaults to `http://localhost:5000/api`. |

Example local backend configuration with placeholders:

```dotenv
# backend/.env
SECRET_KEY=replace-with-a-long-random-secret
JWT_SECRET_KEY=replace-with-a-different-long-random-secret
DATABASE_URL=postgresql+psycopg2://gym_user:YOUR_PASSWORD@localhost:5432/gym_db
CORS_ORIGINS=http://localhost:5173
```

Optional frontend override:

```dotenv
# frontend/.env
VITE_API_URL=http://localhost:5000/api
```

Never publish real credentials, keys, or `.env` contents.

## 17. API Documentation

All endpoints are prefixed with `/api`. Unless marked public, endpoints require `Authorization: Bearer <access-token>`. Role requirements are stated per route group.

| Module | Method | Endpoint | Access |
|---|---|---|---|
| Health | `GET` | `/health` | Public. |
| Authentication | `POST` | `/auth/register` | Public; registers a member and returns a token. |
| Authentication | `POST` | `/auth/login` | Public; authenticates and returns a token. |
| Authentication | `GET` | `/auth/me` | Authenticated; current account. |
| Plans | `GET` | `/plans`, `/plans/{plan_id}` | Public. |
| Plans | `POST`, `PUT`, `DELETE` | `/plans`, `/plans/{plan_id}` | Admin; delete deactivates the plan. |
| Trainers | `GET` | `/trainers`, `/trainers/{trainer_id}` | Public. |
| Trainers | `POST`, `PUT`, `DELETE` | `/trainers`, `/trainers/{trainer_id}` | Admin. |
| Classes | `GET` | `/classes`, `/classes/{class_id}` | Public. |
| Classes | `POST`, `PUT` | `/classes`, `/classes/{class_id}` | Admin or trainer. |
| Classes | `DELETE` | `/classes/{class_id}` | Admin; class must have no bookings. |
| Bookings | `GET`, `POST` | `/bookings` | Authenticated; list own bookings (admin sees all) or create a booking. |
| Bookings | `DELETE` | `/bookings/{booking_id}` | Booking owner or admin; cancels booking. |
| Memberships | `POST` | `/memberships/subscribe` | Authenticated; creates membership and simulated payment. |
| Memberships | `GET` | `/memberships` | Authenticated; own memberships (admin sees all). |
| Payments | `GET` | `/payments` | Authenticated; own payments (admin sees all). |
| Attendance | `POST` | `/attendance/check-in`, `/attendance/check-out` | Member. |
| Attendance | `GET` | `/attendance/me` | Member or admin; returns records for the current account. |
| Attendance | `GET` | `/admin/attendance`, `/admin/attendance/summary` | Admin. |
| Exercises | `GET` | `/exercises` | Authenticated. |
| Workouts | `POST` | `/workouts` | Member or admin; records a session. |
| Workouts | `GET` | `/workouts/me` | Authenticated; current account's sessions, or all sessions for admin. |
| Workouts | `PUT`, `DELETE` | `/workouts/{session_id}` | Owner or admin; trainers cannot edit or delete member sessions. |
| Workout plans | `GET` | `/trainer/workout-plans` | Trainer (own plans) or admin (all plans). |
| Workout plans | `POST` | `/workout-plans` | Trainer or admin. |
| Workouts | `GET` | `/admin/workout-summary` | Admin. |
| Trainer availability | `GET` | `/trainers/{trainer_id}/availability?date=YYYY-MM-DD` | Public. |
| Appointments | `POST` | `/appointments` | Member; requests an appointment. |
| Appointments | `GET` | `/appointments/me` | Authenticated; appointments for current member account. |
| Appointments | `PATCH` | `/appointments/{appointment_id}/cancel` | Appointment owner, assigned trainer, or admin. |
| Appointments | `GET` | `/trainer/appointments` | Trainer (assigned appointments) or admin (all). |
| Appointments | `PATCH` | `/trainer/appointments/{appointment_id}/status` | Assigned trainer or admin. |
| Appointments | `GET` | `/admin/appointments`, `/admin/appointments/summary` | Admin. |
| Admin | `GET` | `/admin/members`, `/admin/plans`, `/admin/trainers`, `/admin/stats` | Admin. |

## 18. Authentication and User Roles

Registration creates a member account. Admins create trainer accounts through trainer-management endpoints. Login and registration return JWT access tokens; the frontend stores the token in browser `localStorage` and attaches it to API requests. Tokens expire after 12 hours.

| Role | Capabilities enforced by backend |
|---|---|
| Member | Book/cancel own classes, subscribe to plans, view own memberships and payments, use attendance routes, manage own workout sessions, and request/cancel own appointments. |
| Trainer | Create/edit classes; view and update assigned appointments; create and list workout plans associated with their trainer profile. |
| Admin | Manage plans, trainers, and classes; view member and business summaries; access admin attendance, workout, and appointment endpoints. |

Authorization differs by endpoint. Frontend route protection controls page access but does not replace backend permission checks.

## 19. Screenshots

There are no application screenshots documented here. Add genuine captures under `docs/screenshots/` and embed them after the files are added; no placeholder images or fake links are used.

Suggested filenames:

```text
docs/screenshots/
├── homepage.png
├── login.png
├── member-dashboard.png
├── admin-dashboard.png
├── membership-plans.png
├── trainers.png
├── classes.png
├── attendance.png
├── workouts.png
└── appointments.png
```

Use non-sensitive demonstration data in screenshots. Do not include real member details, tokens, or credentials.

## 20. Security

- Passwords are hashed using Werkzeug security helpers.
- Protected API routes use JWT bearer tokens with a configured 12-hour expiration.
- Backend role checks restrict administrative and trainer actions; frontend route guards are not the security boundary.
- Set distinct, randomly generated `SECRET_KEY` and `JWT_SECRET_KEY` values in deployment configuration.
- Keep database credentials and `.env` files private; use a least-privilege PostgreSQL role.
- The seed script contains static demo credentials. Use it only with a development database and disable or rotate demo accounts before deployment.
- The frontend stores access tokens in `localStorage`; serve production traffic over HTTPS and protect against script injection.
- Membership payments are simulated and should not be represented as real payment processing.

## 21. Troubleshooting

| Issue | Checks and resolution |
|---|---|
| PostgreSQL connection refused | Ensure the PostgreSQL service is running and verify host, port, database, role, and `DATABASE_URL`. |
| PostgreSQL authentication failure | Confirm the role/password and URL encoding for reserved password characters. Keep credentials only in `backend\.env`. |
| Missing Python package | Activate `backend\venv` and run `python -m pip install -r requirements.txt` from `backend`. |
| `ZoneInfoNotFoundError` on Windows | The attendance model uses `Asia/Kolkata`. Install the optional timezone database with `python -m pip install tzdata` in the active environment. It is not currently listed in `requirements.txt`. |
| CORS error in browser | Set `CORS_ORIGINS` to the exact frontend origin (scheme and port), then restart Flask. Comma-separated origins are supported. |
| Frontend cannot contact API | Run the backend and check `http://localhost:5000/api/health`. Check `VITE_API_URL` and restart Vite after changing its environment. |
| Flask-Migrate cannot find app | From `backend`, activate the virtual environment and set `$env:FLASK_APP = "run.py"`. Initialize migrations with `flask db init` only when no migrations directory exists. |
| Tables do not match model changes | `db.create_all()` does not update existing tables. Generate/review a Flask-Migrate revision and apply it with `flask db upgrade`; do not drop tables as a routine fix. |
| Login or protected route fails | Verify the account and role, API URL, and token validity. Tokens expire after 12 hours; log in again if expired. |

## 22. Future Improvements

These are potential enhancements, not implemented features:

- QR-code attendance.
- Expanded analytics and reporting.
- Diet and nutrition management.
- Member progress tracking.
- Notifications for bookings, appointments, and memberships.
- Integration with a real payment provider.
- A dedicated trainer dashboard.

## 23. Developer Information

- **Developer:** Dileep Gowda
- **Project:** College DBMS Mini Project
- **License:** No `LICENSE` file is present in the repository; no open-source license is stated.

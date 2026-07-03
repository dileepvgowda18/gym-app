# IronCore Gym — Full-Stack Membership Platform

A complete gym management website: React frontend, Flask REST API backend,
PostgreSQL database. Public marketing pages, member dashboard (bookings,
membership, payment history), and an admin panel (members, plans, trainers,
classes, revenue stats).

```
gym-app/
├── backend/     Flask API + PostgreSQL (SQLAlchemy models, JWT auth)
└── frontend/    React (Vite) app
```

## 1. Backend setup

### Requirements
- Python 3.10+
- PostgreSQL running locally (or a hosted instance, e.g. Render/Supabase/Railway)

### Create the database
```sql
CREATE USER gym_user WITH PASSWORD 'gym_password';
CREATE DATABASE gym_db OWNER gym_user;
```

### Install & configure
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # edit DATABASE_URL / secrets if needed
```

### Create tables + demo data
```bash
python seed.py
```
This creates all tables and seeds:
- Admin login: `admin@ironcore.gym` / `admin123`
- 3 membership plans (Starter, Pro, Elite)
- 3 trainers with logins (password: `trainer123`)
- 5 weekly classes

### Run the API
```bash
python run.py
```
API runs at `http://localhost:5000`. Health check: `GET /api/health`.

## 2. Frontend setup

### Requirements
- Node.js 18+

### Install & run
```bash
cd frontend
npm install
npm run dev
```
App runs at `http://localhost:5173` and talks to the API via `VITE_API_URL`
in `.env` (defaults to `http://localhost:5000/api`).

### Production build
```bash
npm run build
```
Outputs static files to `frontend/dist` — deploy to Vercel/Netlify, or serve
with any static host.

## 3. API overview

| Area        | Endpoints |
|-------------|-----------|
| Auth        | `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me` |
| Plans       | `GET /api/plans`, `POST/PUT/DELETE /api/plans/:id` (admin) |
| Trainers    | `GET /api/trainers`, `POST/PUT/DELETE /api/trainers/:id` (admin) |
| Classes     | `GET /api/classes`, `POST/PUT/DELETE /api/classes/:id` (admin/trainer) |
| Bookings    | `GET/POST /api/bookings`, `DELETE /api/bookings/:id` |
| Memberships | `POST /api/memberships/subscribe`, `GET /api/memberships` |
| Payments    | `GET /api/payments` |
| Admin       | `GET /api/admin/members`, `GET /api/admin/stats` |

All protected routes expect `Authorization: Bearer <token>`, issued at
login/register. Roles: `member`, `trainer`, `admin`.

## 4. Notes & next steps

- **Payments**: `subscribe` simulates a successful payment and records a
  transaction. Swap in real Stripe/Razorpay checkout by replacing the logic
  in `backend/app/routes/payments.py`.
- **Migrations**: `Flask-Migrate` is wired up. After the first `seed.py`
  run, use `flask db init/migrate/upgrade` for schema changes going forward
  instead of `create_all()`.
- **Deployment**: backend → Render/Railway (set `DATABASE_URL`,
  `SECRET_KEY`, `JWT_SECRET_KEY`, `CORS_ORIGINS` env vars); frontend →
  Vercel/Netlify with `VITE_API_URL` pointing at your deployed API.
- **Security**: change all default passwords and secrets before going live.

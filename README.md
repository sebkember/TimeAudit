# TimeAudit

A full-stack AI-powered time tracking web app for students and professionals. Track your time, manage tasks, get AI-generated schedules, and analyse your productivity through charts and statistics — no sign-up required to start.

**Live at: [timeaudit.net](https://timeaudit.net)**

---

## Features

- **Frictionless time tracking** — start/stop activities with one click, or log past ones manually
- **AI scheduling** — OpenAI-powered schedule generation based on your tasks and past activity patterns
- **Task tracking** — add tasks with deadlines and durations, link activities to tasks to track progress
- **Statistics dashboard** — pie charts and bar charts breaking down time by activity, category, and day
- **Streak system** — daily streak tracking to encourage consistent use
- **No sign-up required** — data stored in `localStorage` for unauthenticated users, synced to the server on login/signup
- **Persistent accounts** — JWT-authenticated sessions with HttpOnly cookies, bcrypt password hashing

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Database | SQLite |
| Auth | JWT, bcrypt |
| AI | OpenAI API |
| Frontend | Vanilla JS, HTML, CSS |
| Charts | Chart.js |
| Rate limiting | Flask-Limiter |

---

## Architecture

```
timeaudit/
├── main.py                  # Flask app: all routes and database logic
├── templates/
│   ├── index.html           # Landing page
│   ├── calendar.html        # Main time tracking view
│   ├── goals.html           # Task management
│   ├── statistics.html      # Analytics dashboard
│   ├── login.html           # Login page
│   └── signup.html          # Signup page
└── static/
    ├── calendar.js          # Calendar/activity tracking logic
    ├── goals.js             # Task management logic
    ├── statistics.js        # Chart rendering and data fetching
    ├── login.js             # Login, localStorage sync on auth
    ├── signup.js            # Signup and initial data upload
    ├── index.js             # Landing page auth redirect
    └── style.css            # Global styles
```

### Data Flow

Users can use the app without an account — all data is held in `localStorage`. On login or signup, local data is synced to the server via dedicated `/api/*/sync` endpoints, then overwritten with the canonical server state. Authenticated sessions use HttpOnly JWT cookies.

### Database Schema

```
User         — UserID, Email, PasswordHash, Streak
Activity     — ActivityID, Title, CategoryID, StartTime, EndTime, Date, GoalID, UserID, Running
ScheduledActivity — ScheduledActivityID, Title, CategoryID, StartTime, EndTime, Date, UserID
Goal         — GoalID, Title, Duration, TimeDone, Date, UserID
Category     — CategoryID, Name, Colour
Session      — SessionID, Token, UserID, CreatedAt, ExpiresAt, Revoked
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| GET/POST | `/api/activities` | Fetch or add activities |
| POST | `/api/activities/sync` | Sync localStorage activities to server |
| POST | `/api/activities/edit` | Update an existing activity |
| POST | `/api/activities/remove` | Delete an activity |
| GET/POST | `/api/activities/running` | Get or set the currently running activity |
| GET/POST | `/api/goals` | Fetch or add goals |
| POST | `/api/goals/sync` | Sync localStorage goals to server |
| POST | `/api/goals/remove` | Delete a goal |
| GET/POST | `/api/scheduled-activities` | Fetch or add scheduled activities |
| POST | `/api/scheduled-activities/sync` | Sync scheduled activities to server |
| GET | `/api/auth` | Check authentication status |
| POST | `/api/generate-schedule` | Generate AI schedule via OpenAI |

---

## Running Locally

### Prerequisites

- Python 3.10+
- An OpenAI API key

### Setup

```bash
git clone https://github.com/sebkember/TimeAudit
cd TimeAudit
pip install -r requirements.txt
```

Create a `.env` file:

```
SECRET_KEY=your_secret_key_here
OPENAI_API_KEY=your_openai_key_here
```

Initialise the database (uncomment the line in `main.py`):

```python
# In main.py, temporarily uncomment:
initialise_database()
```

Then run:

```bash
python main.py
```

The app will be available at `http://localhost:5000`.

---

## Deployment

The app is deployed on a Linux VPS with Nginx as a reverse proxy in front of Gunicorn. HTTPS is handled via Let's Encrypt.

---

## Known Limitations / Roadmap

- [ ] Cookie domain is currently hardcoded (`192.168.1.162`) — should be environment-variable-driven
- [ ] `initialise_database()` must be manually uncommented on first run
- [ ] Rate limiting is initialised but not applied to individual routes
- [ ] No password reset / forgot password flow

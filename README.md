# Duty Check-In Board

A small Flask web app that replaces a pen-and-paper sign-in sheet.
Staff can check in .

## Features
- Session-based login with hashed passwords (Flask-Login + Werkzeug)
- Dashboard showing every employee's current status (On Duty / Off Duty)
- One-click check-in / check-out with a timestamp
- SQLite database — no external DB server needed

## Setup

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize the database with demo data
flask --app app init-db

# 4. Run the app
flask --app app run --debug
```

Then open **http://127.0.0.1:5000** in your browser.

**Demo login:** `admin` / `admin123`

## Project structure

```
duty-checkin/
├── app.py                 # Routes, models, app setup
├── requirements.txt
├── templates/
│   ├── base.html           # Shared layout
│   ├── login.html
│   └── dashboard.html
└── static/
    └── style.css
```

## How it works

- **`User`** model — staff accounts that can log in (separate from the
  employees shown on the board, so you could restrict who's allowed to
  edit the board vs. just viewing it).
- **`Employee`** model — the people tracked on the duty board, with an
  `on_duty` boolean and a `last_updated` timestamp.
- Logging in is required to view `/dashboard` (`@login_required`).
- Clicking "Check In" / "Check Out" POSTs to `/checkin/<id>`, which flips
  the employee's status and updates the timestamp.

## Possible next steps (good talking points for an interview)
- Separate "admin" vs "employee" roles/permissions
- A `/history` page logging every check-in/out event, not just current status
- Employee self-service: each employee logs in and can only toggle their
  own status
- Deploy it (Render, Railway, Fly.io) so it's a live demo link, not just a repo
- Swap SQLite for Postgres when moving beyond a single-file demo

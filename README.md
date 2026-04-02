# 🎓 AttendPro – Student Attendance Management System

A full-stack web application for managing student attendance across multiple classes — built with **Python Flask**, **SQLite**, and **Vanilla JS**.

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python) ![Flask](https://img.shields.io/badge/Flask-3.0-black?logo=flask) ![SQLite](https://img.shields.io/badge/Database-SQLite-lightblue?logo=sqlite) ![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- 🔐 **Login System** – Admin & Teacher roles with hashed passwords
- 🏫 **Class Management** – Add, edit, delete classes
- 👨‍🎓 **Student Management** – Add, edit, delete students with roll numbers
- ✅ **Mark Attendance** – Present / Absent / Leave per student (bulk form)
- 📋 **Attendance History** – Filter by class, student, date, or status
- 📊 **Dashboard** – Live stats, per-class breakdown, 7-day trend
- 📥 **Export CSV** – Download filtered attendance records
- 📱 **Responsive UI** – Dark glassmorphism design, works on mobile

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/attendance-system.git
cd attendance-system

# 2. Install dependencies
python -m pip install -r requirements.txt

# 3. Run the app
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

> **Windows users:** You can also just double-click `run.bat`

---

## 🔑 Default Login Credentials

| Username | Password | Role |
|---|---|---|
| `admin` | `admin123` | Administrator |
| `teacher1` | `teacher123` | Teacher |

---

## 📁 Project Structure

```
attendance_system/
├── app.py              # Flask entry point
├── database.py         # SQLite schema + seed data
├── requirements.txt    # Dependencies
├── run.bat             # One-click Windows launcher
├── routes/
│   ├── auth.py         # Login / logout
│   ├── students.py     # Student CRUD
│   ├── classes.py      # Class CRUD
│   ├── attendance.py   # Mark & view attendance
│   ├── dashboard.py    # Stats API
│   └── export.py       # CSV export
├── templates/          # Jinja2 HTML pages
└── static/css/         # Stylesheet
```

---

## 🗄️ Sample Data

The database auto-seeds with **3 classes** and **11 students** on first run — no setup needed.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3 + Flask |
| Database | SQLite (via `sqlite3`) |
| Auth | Werkzeug password hashing |
| Frontend | HTML5 + CSS3 + Vanilla JS |

---

## 📄 License

MIT License — free to use, modify, and distribute.

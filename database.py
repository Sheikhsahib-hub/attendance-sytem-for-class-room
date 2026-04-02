"""
database.py
Handles SQLite database initialization, schema creation, and sample data seeding.
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), 'attendance.db')


def get_db():
    """Return a new database connection with row_factory set for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables and seed initial data if the database is fresh."""
    conn = get_db()
    cursor = conn.cursor()

    # ── Users table (admin / teachers) ───────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL,
            role     TEXT    NOT NULL DEFAULT 'teacher',
            name     TEXT    NOT NULL
        )
    """)

    # ── Classes table ──────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS classes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL UNIQUE,
            description TEXT
        )
    """)

    # ── Students table ─────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT    NOT NULL,
            roll_no  TEXT    NOT NULL,
            class_id INTEGER NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
            email    TEXT,
            phone    TEXT,
            UNIQUE(roll_no, class_id)
        )
    """)

    # ── Attendance table ──────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
            class_id   INTEGER NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
            date       TEXT    NOT NULL,
            time       TEXT    NOT NULL,
            status     TEXT    NOT NULL CHECK(status IN ('Present','Absent','Leave')),
            notes      TEXT,
            UNIQUE(student_id, date)
        )
    """)

    conn.commit()

    # ── Seed data (only if tables are empty) ─────────────────────────────────
    _seed_data(cursor, conn)
    conn.close()


def _seed_data(cursor, conn):
    """Insert sample data for testing if the database is empty."""

    # Admin user
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO users (username, password, role, name) VALUES (?, ?, ?, ?)",
            ('admin', generate_password_hash('admin123'), 'admin', 'Administrator')
        )
        cursor.execute(
            "INSERT INTO users (username, password, role, name) VALUES (?, ?, ?, ?)",
            ('teacher1', generate_password_hash('teacher123'), 'teacher', 'Mr. Ahmed')
        )

    # Sample classes
    cursor.execute("SELECT COUNT(*) FROM classes")
    if cursor.fetchone()[0] == 0:
        classes = [
            ('Class A', 'Grade 9 – Section A'),
            ('Class B', 'Grade 9 – Section B'),
            ('Class C', 'Grade 10 – Section A'),
        ]
        cursor.executemany("INSERT INTO classes (name, description) VALUES (?, ?)", classes)

    # Sample students
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        students = [
            # Class A (id=1)
            ('Ali Hassan',     'A001', 1, 'ali@school.com',    '03001111111'),
            ('Sara Khan',      'A002', 1, 'sara@school.com',   '03002222222'),
            ('Usman Tariq',    'A003', 1, 'usman@school.com',  '03003333333'),
            ('Fatima Noor',    'A004', 1, 'fatima@school.com', '03004444444'),
            ('Bilal Ahmed',    'A005', 1, 'bilal@school.com',  '03005555555'),
            # Class B (id=2)
            ('Zara Malik',     'B001', 2, 'zara@school.com',   '03006666666'),
            ('Hassan Raza',    'B002', 2, 'hassan@school.com', '03007777777'),
            ('Ayesha Siddiq',  'B003', 2, 'ayesha@school.com', '03008888888'),
            ('Imran Butt',     'B004', 2, 'imran@school.com',  '03009999999'),
            # Class C (id=3)
            ('Sana Javed',     'C001', 3, 'sana@school.com',   '03010000000'),
            ('Kamran Sheikh',  'C002', 3, 'kamran@school.com', '03011111111'),
        ]
        cursor.executemany(
            "INSERT INTO students (name, roll_no, class_id, email, phone) VALUES (?, ?, ?, ?, ?)",
            students
        )

    conn.commit()

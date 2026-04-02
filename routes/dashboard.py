"""
routes/dashboard.py
Provides aggregated statistics for the dashboard page.
"""

from flask import Blueprint, jsonify, render_template
from datetime import datetime
from database import get_db
from routes.auth import login_required

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@dashboard_bp.route('/api/dashboard', methods=['GET'])
@login_required
def get_stats():
    """Return total students, attendance summary, and today's report per class."""
    today = datetime.now().strftime('%Y-%m-%d')
    db    = get_db()

    # Total students and classes
    total_students = db.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    total_classes  = db.execute("SELECT COUNT(*) FROM classes").fetchone()[0]

    # Overall attendance counts (all time)
    overall = db.execute("""
        SELECT
            SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END) AS present,
            SUM(CASE WHEN status='Absent'  THEN 1 ELSE 0 END) AS absent,
            SUM(CASE WHEN status='Leave'   THEN 1 ELSE 0 END) AS leave
        FROM attendance
    """).fetchone()

    # Today's attendance counts
    today_stats = db.execute("""
        SELECT
            SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END) AS present,
            SUM(CASE WHEN status='Absent'  THEN 1 ELSE 0 END) AS absent,
            SUM(CASE WHEN status='Leave'   THEN 1 ELSE 0 END) AS leave
        FROM attendance WHERE date = ?
    """, (today,)).fetchone()

    # Per-class summary for today
    class_today = db.execute("""
        SELECT c.name AS class_name,
               COUNT(s.id) AS total,
               SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) AS present,
               SUM(CASE WHEN a.status='Absent'  THEN 1 ELSE 0 END) AS absent,
               SUM(CASE WHEN a.status='Leave'   THEN 1 ELSE 0 END) AS leave
        FROM classes c
        LEFT JOIN students s ON s.class_id = c.id
        LEFT JOIN attendance a ON a.student_id = s.id AND a.date = ?
        GROUP BY c.id
        ORDER BY c.name
    """, (today,)).fetchall()

    # Recent 7-day attendance trend
    trend = db.execute("""
        SELECT date,
               SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END) AS present,
               SUM(CASE WHEN status='Absent'  THEN 1 ELSE 0 END) AS absent,
               SUM(CASE WHEN status='Leave'   THEN 1 ELSE 0 END) AS leave
        FROM attendance
        GROUP BY date
        ORDER BY date DESC
        LIMIT 7
    """).fetchall()

    db.close()

    return jsonify({
        'total_students': total_students,
        'total_classes':  total_classes,
        'overall': {
            'present': overall['present'] or 0,
            'absent':  overall['absent']  or 0,
            'leave':   overall['leave']   or 0,
        },
        'today': {
            'date':    today,
            'present': today_stats['present'] or 0,
            'absent':  today_stats['absent']  or 0,
            'leave':   today_stats['leave']   or 0,
        },
        'class_today': [dict(r) for r in class_today],
        'trend':        [dict(r) for r in reversed(trend)],
    })

"""
routes/attendance.py
Endpoints for marking, viewing, and filtering attendance records.
"""

from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
from database import get_db
from routes.auth import login_required

attendance_bp = Blueprint('attendance', __name__)


@attendance_bp.route('/attendance')
@login_required
def attendance_page():
    return render_template('attendance.html')


@attendance_bp.route('/history')
@login_required
def history_page():
    return render_template('history.html')


@attendance_bp.route('/api/attendance', methods=['GET'])
@login_required
def get_attendance():
    """
    Return attendance records.
    Optional query params: date, class_id, student_id
    """
    date       = request.args.get('date')
    class_id   = request.args.get('class_id')
    student_id = request.args.get('student_id')

    query = """
        SELECT a.id, a.date, a.time, a.status, a.notes,
               s.name AS student_name, s.roll_no,
               c.name AS class_name, s.id AS student_id, c.id AS class_id
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        JOIN classes  c ON a.class_id   = c.id
        WHERE 1=1
    """
    params = []
    if date:
        query += " AND a.date = ?"
        params.append(date)
    if class_id:
        query += " AND a.class_id = ?"
        params.append(class_id)
    if student_id:
        query += " AND a.student_id = ?"
        params.append(student_id)

    query += " ORDER BY a.date DESC, c.name, s.name"

    db = get_db()
    rows = db.execute(query, params).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@attendance_bp.route('/api/attendance/bulk', methods=['POST'])
@login_required
def mark_attendance_bulk():
    """
    Mark attendance for multiple students at once.
    Body: { "class_id": int, "date": "YYYY-MM-DD", "records": [{"student_id": int, "status": str, "notes": str}] }
    """
    data     = request.get_json()
    class_id = data.get('class_id')
    date     = data.get('date', datetime.now().strftime('%Y-%m-%d'))
    records  = data.get('records', [])
    time_now = datetime.now().strftime('%H:%M:%S')

    if not class_id or not records:
        return jsonify({'error': 'class_id and records are required'}), 400

    db = get_db()
    saved, updated = 0, 0
    for rec in records:
        student_id = rec.get('student_id')
        status     = rec.get('status', 'Present')
        notes      = rec.get('notes', '')

        # UPSERT: insert or replace if same student+date already recorded
        existing = db.execute(
            "SELECT id FROM attendance WHERE student_id=? AND date=?",
            (student_id, date)
        ).fetchone()

        if existing:
            db.execute(
                "UPDATE attendance SET status=?, notes=?, time=? WHERE id=?",
                (status, notes, time_now, existing['id'])
            )
            updated += 1
        else:
            db.execute(
                "INSERT INTO attendance (student_id, class_id, date, time, status, notes) VALUES (?,?,?,?,?,?)",
                (student_id, class_id, date, time_now, status, notes)
            )
            saved += 1

    db.commit()
    db.close()
    return jsonify({'saved': saved, 'updated': updated}), 201


@attendance_bp.route('/api/attendance/<int:att_id>', methods=['PUT'])
@login_required
def update_attendance(att_id):
    """Edit a single attendance record's status/notes."""
    data   = request.get_json()
    status = data.get('status')
    notes  = data.get('notes', '')

    if status not in ('Present', 'Absent', 'Leave'):
        return jsonify({'error': 'Invalid status'}), 400

    db = get_db()
    db.execute(
        "UPDATE attendance SET status=?, notes=? WHERE id=?",
        (status, notes, att_id)
    )
    db.commit()
    db.close()
    return jsonify({'success': True})


@attendance_bp.route('/api/attendance/<int:att_id>', methods=['DELETE'])
@login_required
def delete_attendance(att_id):
    """Delete a single attendance record."""
    db = get_db()
    db.execute("DELETE FROM attendance WHERE id=?", (att_id,))
    db.commit()
    db.close()
    return jsonify({'success': True})


@attendance_bp.route('/api/attendance/students-for-class', methods=['GET'])
@login_required
def students_for_class():
    """
    Return students in a class with their attendance status for a given date
    (pre-fills the mark-attendance form).
    """
    class_id = request.args.get('class_id')
    date     = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))

    if not class_id:
        return jsonify({'error': 'class_id required'}), 400

    db = get_db()
    rows = db.execute("""
        SELECT s.id, s.name, s.roll_no,
               a.status, a.notes, a.id AS att_id
        FROM students s
        LEFT JOIN attendance a ON a.student_id = s.id AND a.date = ?
        WHERE s.class_id = ?
        ORDER BY s.name
    """, (date, class_id)).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])

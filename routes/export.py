"""
routes/export.py
Exports attendance records to a CSV file.
"""

import csv
import io
from flask import Blueprint, request, make_response
from database import get_db
from routes.auth import login_required

export_bp = Blueprint('export', __name__)


@export_bp.route('/api/export/csv', methods=['GET'])
@login_required
def export_csv():
    """
    Export filtered attendance records as a CSV download.
    Optional query params: date, class_id, student_id
    """
    date       = request.args.get('date')
    class_id   = request.args.get('class_id')
    student_id = request.args.get('student_id')

    query = """
        SELECT a.date, a.time, s.name AS student_name, s.roll_no,
               c.name AS class_name, a.status, a.notes
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

    db   = get_db()
    rows = db.execute(query, params).fetchall()
    db.close()

    # Build CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Time', 'Student Name', 'Roll No', 'Class', 'Status', 'Notes'])
    for row in rows:
        writer.writerow([
            row['date'], row['time'], row['student_name'],
            row['roll_no'], row['class_name'], row['status'],
            row['notes'] or ''
        ])

    filename = f"attendance_export.csv"
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    response.headers['Content-Type']        = 'text/csv; charset=utf-8'
    return response

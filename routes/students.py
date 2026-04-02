"""
routes/students.py
CRUD API endpoints for managing students.
"""

from flask import Blueprint, request, jsonify, render_template
from database import get_db
from routes.auth import login_required

students_bp = Blueprint('students', __name__)


@students_bp.route('/students')
@login_required
def students_page():
    return render_template('students.html')


@students_bp.route('/api/students', methods=['GET'])
@login_required
def get_students():
    """Return all students, optionally filtered by class_id."""
    class_id = request.args.get('class_id')
    db = get_db()
    if class_id:
        rows = db.execute("""
            SELECT s.*, c.name AS class_name
            FROM students s JOIN classes c ON s.class_id = c.id
            WHERE s.class_id = ?
            ORDER BY s.name
        """, (class_id,)).fetchall()
    else:
        rows = db.execute("""
            SELECT s.*, c.name AS class_name
            FROM students s JOIN classes c ON s.class_id = c.id
            ORDER BY c.name, s.name
        """).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@students_bp.route('/api/students/<int:student_id>', methods=['GET'])
@login_required
def get_student(student_id):
    """Return a single student's details."""
    db = get_db()
    row = db.execute("""
        SELECT s.*, c.name AS class_name
        FROM students s JOIN classes c ON s.class_id = c.id
        WHERE s.id = ?
    """, (student_id,)).fetchone()
    db.close()
    if not row:
        return jsonify({'error': 'Student not found'}), 404
    return jsonify(dict(row))


@students_bp.route('/api/students', methods=['POST'])
@login_required
def add_student():
    """Add a new student."""
    data = request.get_json()
    name     = data.get('name', '').strip()
    roll_no  = data.get('roll_no', '').strip()
    class_id = data.get('class_id')
    email    = data.get('email', '').strip()
    phone    = data.get('phone', '').strip()

    if not name or not roll_no or not class_id:
        return jsonify({'error': 'Name, Roll No, and Class are required'}), 400

    db = get_db()
    try:
        cursor = db.execute(
            "INSERT INTO students (name, roll_no, class_id, email, phone) VALUES (?, ?, ?, ?, ?)",
            (name, roll_no, class_id, email, phone)
        )
        db.commit()
        new_id = cursor.lastrowid
    except Exception as e:
        db.close()
        return jsonify({'error': 'Roll number already exists in this class'}), 409
    db.close()
    return jsonify({'id': new_id, 'name': name}), 201


@students_bp.route('/api/students/<int:student_id>', methods=['PUT'])
@login_required
def update_student(student_id):
    """Update a student's details."""
    data = request.get_json()
    name     = data.get('name', '').strip()
    roll_no  = data.get('roll_no', '').strip()
    class_id = data.get('class_id')
    email    = data.get('email', '').strip()
    phone    = data.get('phone', '').strip()

    if not name or not roll_no or not class_id:
        return jsonify({'error': 'Name, Roll No, and Class are required'}), 400

    db = get_db()
    try:
        db.execute(
            "UPDATE students SET name=?, roll_no=?, class_id=?, email=?, phone=? WHERE id=?",
            (name, roll_no, class_id, email, phone, student_id)
        )
        db.commit()
    except Exception as e:
        db.close()
        return jsonify({'error': str(e)}), 409
    db.close()
    return jsonify({'success': True})


@students_bp.route('/api/students/<int:student_id>', methods=['DELETE'])
@login_required
def delete_student(student_id):
    """Delete a student and their attendance records."""
    db = get_db()
    db.execute("DELETE FROM students WHERE id=?", (student_id,))
    db.commit()
    db.close()
    return jsonify({'success': True})

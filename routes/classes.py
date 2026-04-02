"""
routes/classes.py
CRUD API endpoints for managing classes.
"""

from flask import Blueprint, request, jsonify, render_template
from database import get_db
from routes.auth import login_required

classes_bp = Blueprint('classes', __name__)


@classes_bp.route('/classes')
@login_required
def classes_page():
    return render_template('classes.html')


@classes_bp.route('/api/classes', methods=['GET'])
@login_required
def get_classes():
    """Return all classes with student count."""
    db = get_db()
    rows = db.execute("""
        SELECT c.id, c.name, c.description,
               COUNT(s.id) AS student_count
        FROM classes c
        LEFT JOIN students s ON s.class_id = c.id
        GROUP BY c.id
        ORDER BY c.name
    """).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@classes_bp.route('/api/classes', methods=['POST'])
@login_required
def add_class():
    """Add a new class."""
    data = request.get_json()
    name = data.get('name', '').strip()
    desc = data.get('description', '').strip()
    if not name:
        return jsonify({'error': 'Class name is required'}), 400

    db = get_db()
    try:
        cursor = db.execute(
            "INSERT INTO classes (name, description) VALUES (?, ?)", (name, desc)
        )
        db.commit()
        new_id = cursor.lastrowid
    except Exception as e:
        db.close()
        return jsonify({'error': str(e)}), 409
    db.close()
    return jsonify({'id': new_id, 'name': name, 'description': desc}), 201


@classes_bp.route('/api/classes/<int:class_id>', methods=['PUT'])
@login_required
def update_class(class_id):
    """Update class name/description."""
    data = request.get_json()
    name = data.get('name', '').strip()
    desc = data.get('description', '').strip()
    if not name:
        return jsonify({'error': 'Class name is required'}), 400

    db = get_db()
    db.execute(
        "UPDATE classes SET name=?, description=? WHERE id=?", (name, desc, class_id)
    )
    db.commit()
    db.close()
    return jsonify({'success': True})


@classes_bp.route('/api/classes/<int:class_id>', methods=['DELETE'])
@login_required
def delete_class(class_id):
    """Delete a class (cascades to students and attendance)."""
    db = get_db()
    db.execute("DELETE FROM classes WHERE id=?", (class_id,))
    db.commit()
    db.close()
    return jsonify({'success': True})

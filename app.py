"""
app.py
Main Flask application entry point.
Registers all blueprints and initializes the database on first run.
"""

from flask import Flask, redirect, url_for, session
from database import init_db
from routes.auth import auth_bp
from routes.students import students_bp
from routes.classes import classes_bp
from routes.attendance import attendance_bp
from routes.dashboard import dashboard_bp
from routes.export import export_bp

app = Flask(__name__)
app.secret_key = 'attendance_secret_key_2024'  # Change in production!

# ── Register blueprints ───────────────────────────────────────────────────────
app.register_blueprint(auth_bp)
app.register_blueprint(students_bp)
app.register_blueprint(classes_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(export_bp)


@app.route('/')
def index():
    """Redirect root to dashboard (login required) or login."""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return redirect(url_for('dashboard.dashboard'))


if __name__ == '__main__':
    init_db()           # Create tables and seed sample data
    app.run(debug=True, port=5000)

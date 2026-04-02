"""
routes/auth.py
Authentication routes: login and logout.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from database import get_db

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    """Decorator: redirect to login if user is not authenticated."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle login form submission and session creation."""
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        db.close()

        if user and check_password_hash(user['password'], password):
            session['user_id']   = user['id']
            session['username']  = user['username']
            session['role']      = user['role']
            session['user_name'] = user['name']
            return redirect(url_for('dashboard.dashboard'))
        else:
            error = 'Invalid username or password.'

    return render_template('login.html', error=error)


@auth_bp.route('/logout')
def logout():
    """Clear session and redirect to login."""
    session.clear()
    return redirect(url_for('auth.login'))

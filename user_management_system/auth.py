from functools import wraps
from flask import session, redirect, url_for, request
from werkzeug.security import check_password_hash
import os


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated


def check_credentials(username, password):
    valid_username = os.environ.get('APP_USERNAME', 'admin')
    valid_hash = os.environ.get('APP_PASSWORD_HASH', '')
    return username == valid_username and check_password_hash(valid_hash, password)

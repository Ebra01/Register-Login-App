from flask import Blueprint, jsonify, request, abort
from flask_login import current_user, logout_user
from flaskr.Models.models import Users
from .utils import addUserToDB, validate_current_user
from flaskr import login_manager

users = Blueprint('users', __name__)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@users.route('/api/user/load')
def load_user_request():

    if current_user.is_authenticated:
        current = current_user.display()
    else:
        current = None

    return jsonify({
        "current_user": current
    })


@users.route('/api/users')
def get_users():
    return jsonify({
        'users': [u.display() for u in Users.query.all()],
        'success': True
    })


@users.route('/api/users/<int:user_id>')
def get_user(user_id):
    user = Users.query.get(user_id)
    if not user:
        abort(404, f'No User Found with ID #{user_id}')

    return jsonify({
        'user': user.display(),
        'success': True
    })


@users.route('/api/register', methods=['GET', 'POST'])
def register():
    # Check if there is a user logged-in already
    if current_user.is_authenticated:
        abort(400, 'You Are Logged-In Already, Logout to Register a New Account!')

    req = request.get_json()

    if not req:
        abort(400, 'Please Provide a Username, Email and Password')

    username = req.get('username')
    email = req.get('email')
    password = req.get('password')

    if not username or not email or not password:
        abort(400, 'Username, Email, and Password Must be Filled!')

    body = {
        'username': username,
        'email': email,
        'password': password
    }

    try:
        addUserToDB(body)
    except Exception as e:
        print(e)
        abort(422, e)

    return jsonify({
        'user': f'User {username} Was Registered Successfully!',
        'success': True
    })


@users.route('/api/logout')
def logout():
    # Check if Someone is logged-in
    if not current_user.is_authenticated:
        abort(400, 'You Are Not Logged-In!')

    username = current_user.username
    # Try to logout user from login_manager
    try:
        logout_user()
    except Exception as e:
        print(e)
        abort(500, 'Something Went Wrong in Our End!')

    return jsonify({
        'user': f'User {username} Logged Out Successfully!',
        'success': True
    })


@users.route('/api/login', methods=['GET', 'POST'])
def login():

    # Check if there is a user logged-in already
    if current_user.is_authenticated:
        abort(400, 'You Are Logged-In Already!')

    req = request.get_json()

    if not req:
        abort(400, 'Please Provide a Username or an Email and Password')

    cred = req.get('usernameOrEmail')
    password = req.get('password')

    try:
        validate_current_user(cred=cred, passw=password)
    except Exception as e:
        print(e)
        abort(422, e)
    return jsonify({
        'user': f'User {current_user.username} Logged-In Successfully!',
        'current_user': current_user.display(),
        'success': True
    })

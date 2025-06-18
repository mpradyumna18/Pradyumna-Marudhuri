from flask import render_template, request, redirect, url_for, session, flash
from . import auth_bp
from flask_bcrypt import Bcrypt
from db import users_col

bcrypt = Bcrypt()

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        if users_col.find_one({'email': email}):
            flash("Email already exists!")
            return redirect(url_for('auth.register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        users_col.insert_one({
            'username': username,
            'email': email,
            'password': hashed_password,
            'role': 'user'  # default role
        })

        flash('Registration successful. Please login.')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        user = users_col.find_one({'email': email})

        if user and bcrypt.check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            session['role'] = user.get('role', 'user')

            flash("Login successful!")
            return redirect(url_for('quiz.dashboard'))
        else:
            flash('Invalid email or password')
            return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for('auth.login'))

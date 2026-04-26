from flask import Flask, render_template, request, redirect, session, url_for, flash
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# Connect to MongoDB
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client['banking_system']
users = db['users']

# Ensure unique index on account_number
users.create_index('account_number', unique=True)


def validate_account_number(acc):
    """Account number: 6-20 alphanumeric characters."""
    return bool(re.match(r'^[A-Za-z0-9]{6,20}$', acc))


def get_logged_in_user():
    if 'account_number' not in session:
        return None
    return users.find_one({'account_number': session['account_number']})


@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        account_number = request.form.get('account_number', '').strip()
        password = request.form.get('password', '')
        balance_str = request.form.get('balance', '0')

        # Validate inputs
        if not name or len(name) < 2:
            flash('Name must be at least 2 characters.', 'error')
            return render_template('register.html')

        if not validate_account_number(account_number):
            flash('Account number must be 6-20 alphanumeric characters.', 'error')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('register.html')

        try:
            balance = float(balance_str)
            if balance < 0:
                raise ValueError
        except ValueError:
            flash('Initial balance must be a non-negative number.', 'error')
            return render_template('register.html')

        # Check duplicate
        if users.find_one({'account_number': account_number}):
            flash('Account number already exists. Choose another.', 'error')
            return render_template('register.html')

        # Hash password before storing
        hashed_pw = generate_password_hash(password)

        users.insert_one({
            'name': name,
            'account_number': account_number,
            'password': hashed_pw,
            'balance': round(balance, 2)
        })

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'account_number' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        account_number = request.form.get('account_number', '').strip()
        password = request.form.get('password', '')

        user = users.find_one({'account_number': account_number})

        # check_password_hash prevents timing attacks
        if user and check_password_hash(user['password'], password):
            session['account_number'] = user['account_number']
            flash(f"Welcome back, {user['name']}!", 'success')
            return redirect(url_for('dashboard'))

        flash('Invalid account number or password.', 'error')
        return render_template('login.html')

    return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    user = get_logged_in_user()
    if not user:
        flash('Please log in to continue.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        action = request.form.get('action')
        amount_str = request.form.get('amount', '0')

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            flash('Amount must be a positive number.', 'error')
            return redirect(url_for('dashboard'))

        amount = round(amount, 2)

        if action == 'deposit':
            users.update_one(
                {'account_number': user['account_number']},
                {'$inc': {'balance': amount}}
            )
            flash(f'₹{amount:,.2f} deposited successfully.', 'success')

        elif action == 'withdraw':
            # Fresh read to avoid stale balance
            fresh_user = users.find_one({'account_number': user['account_number']})
            if fresh_user['balance'] < amount:
                flash('Insufficient balance for withdrawal.', 'error')
            else:
                users.update_one(
                    {'account_number': user['account_number']},
                    {'$inc': {'balance': -amount}}
                )
                flash(f'₹{amount:,.2f} withdrawn successfully.', 'success')
        else:
            flash('Invalid action.', 'error')

        return redirect(url_for('dashboard'))

    # Fresh read on GET
    user = users.find_one({'account_number': session['account_number']})
    return render_template('dashboard.html', user=user)


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode)
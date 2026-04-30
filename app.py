from flask import Flask, render_template, request, redirect, session, url_for, flash
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re

app = Flask(__name__)

# SECRET KEY (important for sessions)
app.secret_key = os.environ.get('SECRET_KEY', 'supersecretkey')


# ================== MONGODB CONNECTION ==================
MONGO_URI = os.environ.get('MONGO_URI')

if not MONGO_URI:
    raise Exception("MONGO_URI not set in environment variables")

client = MongoClient(MONGO_URI)

# Database (IMPORTANT: same as Atlas)
db = client['bankDB']
users = db['users']

# Unique index
users.create_index('account_number', unique=True)


# ================== HELPER FUNCTIONS ==================

def validate_account_number(acc):
    return bool(re.match(r'^[A-Za-z0-9]{6,20}$', acc))


def get_logged_in_user():
    if 'account_number' not in session:
        return None
    return users.find_one({'account_number': session['account_number']})


# ================== ROUTES ==================

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

        # Validation
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

        # Duplicate check
        if users.find_one({'account_number': account_number}):
            flash('Account number already exists.', 'error')
            return render_template('register.html')

        # Hash password
        hashed_pw = generate_password_hash(password)

        users.insert_one({
            'name': name,
            'account_number': account_number,
            'password': hashed_pw,
            'balance': round(balance, 2)
        })

        flash('Account created successfully!', 'success')
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

        if user and check_password_hash(user['password'], password):
            session['account_number'] = user['account_number']
            flash(f"Welcome {user['name']}!", 'success')
            return redirect(url_for('dashboard'))

        flash('Invalid credentials.', 'error')
        return render_template('login.html')

    return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    user = get_logged_in_user()

    if not user:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        action = request.form.get('action')
        amount_str = request.form.get('amount', '0')

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            flash('Enter valid amount.', 'error')
            return redirect(url_for('dashboard'))

        amount = round(amount, 2)

        if action == 'deposit':
            users.update_one(
                {'account_number': user['account_number']},
                {'$inc': {'balance': amount}}
            )
            flash(f'₹{amount} deposited.', 'success')

        elif action == 'withdraw':
            fresh_user = users.find_one({'account_number': user['account_number']})

            if fresh_user['balance'] < amount:
                flash('Insufficient balance.', 'error')
            else:
                users.update_one(
                    {'account_number': user['account_number']},
                    {'$inc': {'balance': -amount}}
                )
                flash(f'₹{amount} withdrawn.', 'success')

        return redirect(url_for('dashboard'))

    user = users.find_one({'account_number': session['account_number']})
    return render_template('dashboard.html', user=user)


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))


# ================== RUN APP ==================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
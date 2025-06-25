from flask import Flask, render_template, request, redirect, session, url_for
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['banking_system']
users = db['users']

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        account_number = request.form['account_number']
        password = request.form['password']
        balance = float(request.form['balance'])

        existing_user = users.find_one({'account_number': account_number})
        if existing_user:
            return 'Account already exists!'

        users.insert_one({
            'name': name,
            'account_number': account_number,
            'password': password,
            'balance': balance
        })
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        account_number = request.form['account_number']
        password = request.form['password']

        user = users.find_one({'account_number': account_number, 'password': password})
        if user:
            session['account_number'] = user['account_number']
            return redirect(url_for('dashboard'))
        return 'Invalid Credentials!'
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'account_number' not in session:
        return redirect(url_for('login'))

    user = users.find_one({'account_number': session['account_number']})

    if request.method == 'POST':
        action = request.form['action']
        amount = float(request.form['amount'])

        if action == 'deposit':
            users.update_one({'account_number': user['account_number']}, {'$inc': {'balance': amount}})
        elif action == 'withdraw' and user['balance'] >= amount:
            users.update_one({'account_number': user['account_number']}, {'$inc': {'balance': -amount}})
        else:
            return 'Insufficient balance'

        return redirect(url_for('dashboard'))

    user = users.find_one({'account_number': session['account_number']})
    return render_template('dashboard.html', user=user)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

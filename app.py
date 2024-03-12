from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
from flask_bcrypt import Bcrypt
from db import *
from bson.objectid import ObjectId
from bson import ObjectId
from bson.json_util import dumps
import os
from datetime import datetime
# previous url mongodb://mongo:27017/

app = Flask(__name__)
# The default URI will be used if the 'MONGO_URI' environment variable is not set
default_mongo_uri = "mongodb://host.docker.internal:27017/"  # Default for kind cluster
app.secret_key = os.getenv('SECRET_KEY', 'your_fallback_secret_key_here')
bcrypt = Bcrypt(app)

# Read 'MONGO_URI' from environment, or use the default if it's not set
mongo_uri = os.getenv('MONGO_URI', default_mongo_uri)
client = MongoClient(mongo_uri)
db = client["expenses_tracker_db"]
users_collection = db["users"]
expenses_collection = db["expenses"]  # Define the expenses collection

@app.route('/')
def home():
    # Directly using users_collection as defined in db.py
    user_docs = users_collection.find({}, {'_id': 0, 'username': 1})
    user_list = [user_doc['username'] for user_doc in user_docs]
    return render_template('home.html', user_list=user_list)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username is None or password is None or len(username) < 4 or len(password) < 4:
            flash('Username and password must be at least 4 characters long.', 'error')
            return render_template('register.html')

        # Hash the password using Bcrypt
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        registration_result = register_user(username, password_hash)  # Pass the hashed password
        if registration_result == 'success':
            # The user is registered, now log them in and redirect to the dashboard
            user = find_user_by_username(username)
            session['username'] = username
            session['user_id'] = str(user['_id'])  # Convert ObjectId to string
            flash('Registration successful! Welcome to your dashboard.', 'success')
            return redirect(url_for('dashboard'))
        elif registration_result == 'exists':
            flash('That username already exists!', 'error')
        elif registration_result == 'error':
            flash('An unexpected error occurred. Please try again later.', 'error')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = find_user_by_username(username)  # Retrieve the user document
        if user:
            # Use bcrypt to check the hashed password
            if bcrypt.check_password_hash(user['password'], password):
                session['username'] = username
                session['user_id'] = str(user['_id'])  # Store user ID in session
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username/password combination', 'error')
        else:
            flash('Username does not exist', 'error')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('Please log in to access the dashboard.', 'info')
        return redirect(url_for('login'))

    user_id = session.get('user_id')  # Assuming you store the user_id in the session upon login
    if not user_id:
        flash('User not found. Please log in again.', 'error')
        return redirect(url_for('login'))

    # Fetch the user's expenses for the current month
    expenses = get_user_expenses(user_id)
    
    return render_template('dashboard.html', username=session.get('username'), expenses=expenses)

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if 'username' not in session:
        flash('Please log in to access this feature.', 'info')
        return redirect(url_for('login'))

    if request.method == 'POST':
        category = request.form.get('category')
        amount = request.form.get('amount')
        date = request.form.get('date')
        notes = request.form.get('notes', '')

        if not category or not amount or not date:
            flash('All fields are required.', 'error')
            return render_template('add_expense.html')

        # Process form data and add the expense
        try:
            # Convert amount to float and date to a datetime object
            amount = float(amount)
            date = datetime.strptime(date, '%Y-%m-%d')
            
            # Get the user_id from the username
            user_id = get_user_id(session['username'])
            
            if user_id:
                # Add expense to the database
                expense_id = add_expense_to_db(user_id, category, amount, date, notes)
                if expense_id:
                    flash('Expense added successfully!', 'success')
                    return redirect(url_for('dashboard'))  # Redirect to the dashboard after successful addition
                else:
                    flash('Failed to add expense.', 'error')
            else:
                flash('User not found.', 'error')
        except ValueError as e:
            flash(f'Invalid input: {str(e)}', 'error')

    # GET request or POST request with error will show the add_expense page again
    return render_template('add_expense.html')

@app.route('/get_expense_data')
def get_expense_data():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    user_id = get_user_id(session['username'])
    if user_id is None:
        return jsonify({'error': 'User not found'}), 404

    expenses = list(expenses_collection.find({'user_id': user_id}, {'_id': 0, 'user_id': 0}))
    return Response(dumps(expenses), mimetype='application/json')

@app.route('/expense_data_by_category')
def expense_data_by_category():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = get_user_id(session['username'])
    if not user_id:
        return jsonify({'error': 'User not found'}), 404

    pipeline = [
        {"$match": {"user_id": ObjectId(user_id)}},
        {"$group": {
            "_id": "$category",
            "total": {"$sum": "$amount"}
        }},
        {"$project": {"_id": 0, "category": "$_id", "total": 1}},
        {"$sort": {"total": -1}}
    ]
    expenses_by_category = list(expenses_collection.aggregate(pipeline))
    return Response(dumps(expenses_by_category), mimetype='application/json')

@app.route('/remove_expense/<expense_id>', methods=['POST'])
def remove_expense(expense_id):
    # Convert the expense_id from string to UUID format if necessary
    # If your expense_id is already a UUID string, you can skip the conversion
    try:
        # Validate that the expense_id is a valid UUID
        valid_expense_id = str(uuid.UUID(expense_id))
    except ValueError as e:
        # If the expense_id is not a valid UUID, return an error response
        return jsonify({'success': False, 'error': 'Invalid expense ID'}), 400

    # Call the remove_expense_from_db function with the valid UUID string
    if remove_expense_from_db(valid_expense_id):
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False, 'error': 'Failed to delete expense'}), 500

@app.route('/remove_account', methods=['POST'])
def remove_account():
    if 'username' in session:
        username = session['username']
        # Assuming you're storing the username in the session and have a method to find the user ID by username
        user_id = get_user_id(username)
        result = users_collection.delete_one({'_id': ObjectId(user_id)})
        if result.deleted_count > 0:
            session.clear()  # Clear the session
            flash('Account successfully removed.', 'success')
            return redirect(url_for('home'))  # Redirect to the home page
        else:
            flash('Account could not be found.', 'error')
            return redirect(url_for('dashboard'))
    else:
        flash('You need to be logged in to remove an account.', 'error')
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

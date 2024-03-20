from APP import getCursor, login_manager
from flask import Blueprint
from flask import render_template, request, redirect, url_for, flash
from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user
from datetime import datetime
import bcrypt
import random
import string
import re


auth_bp = Blueprint('auth', __name__)


# Define a User class for managing user data and authentication

class User (UserMixin):
    def __init__(self, role, id, unum, password):
        self.role = role
        self.id = id
        self.user_num = unum
        self.password = password

    #Returns a unique ID combining the table type and user ID.
    def get_id (self):
        user_id = f"{self.role}-{self.id}"
        return user_id
        
    # Returns True if the user is authenticated.
    def is_authenticated(self):
        return True


# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    connection = getCursor()
    print(f"Loading user with ID: {user_id}")

    if '-' not in user_id:
        print("Unexpected user_id format.")
        return None
    
    role, id = user_id.split('-')
    id = int(id)

    print(f"Extracted: {role} and ID: {id}")


    if role == 'customer':
        user_id_query = """SELECT position, customerID, userNo, PasswordHash FROM customer WHERE customerID = %s;"""
    elif role == 'planner':
        user_id_query = """SELECT position, plannerID, userNo, Password FROM planner WHERE plannerID = %s;"""
    elif role == "admin":
        user_id_query = """SELECT position, adminID, userNo, password FROM admin WHERE adminID = %s;"""
    else:
        print(f"Unexpected table value: {role}")
        return None
    
    connection.execute(user_id_query, (id,))
    user = connection.fetchone()
    if user:
        print(f"Found user: {user}")
        return User(role=role, id=user[1], unum=user[2], password=user[3])
    else:
        print("No user found in database for the given ID.")
    
    return None



# Registration route
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        title = request.form['title']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        # Check if the password meets the criteria
        if not is_valid_password(password):
            flash('Password must be at least 8 digit with both letters and numbers.')
            return render_template('auth/register.html')
        
        connection = getCursor()
        connection.execute("""SELECT email FROM customer WHERE email = %s;""", (email,))
        existing_email = connection.fetchone()

        if existing_email is not None:
            if existing_email:
                flash('The email has already been taken. Please try with another one!')
            return render_template('auth/register.html')
        else:
            hashedp = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            user_no = "c" + ''.join(random.choices(string.digits, k = 5))

            connection = getCursor()
            connection.execute('''INSERT INTO customer (userNo, title, firstName, lastName, position, phone, email, PasswordHash) VALUES (%s, %s, %s, %s,'customer', %s, %s, %s);''',
            (user_no, title, first_name, last_name, phone, email, hashedp))
            flash('Welcome to Plan it Right! Please login now to dicover your favourite venues!')
            return redirect(url_for('auth.login'))
    return render_template('auth/register.html')


# Function to validate the password
def is_valid_password(password):
    if len(password) < 8:
        return False
    if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)', password):
        return False
    return True


# Login route 
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        
        role = "customer"
        connection = getCursor()
        connection.execute("""SELECT position, customerID, userNo, PasswordHash FROM customer WHERE email = %s;""", (email,))
        user = connection.fetchone()

        # Check if the user exists as a customer
        if not user:
            connection.execute("""SELECT position, plannerID, userNo, Password FROM planner WHERE email = %s;""", (email,))
            user = connection.fetchone()
            print(f"After checking planner: {user}")
            if user:
                role = "planner"

        # Check if the user exists as a planner
        if not user:
            connection.execute("""SELECT position, adminID, userNo, Password FROM admin WHERE email = %s;""", (email,))
            user = connection.fetchone()
           
            print(f"After checking admin: {user}")
            if user:
                role = "admin"

        if user:
            # Check if the entered password matches the hashed password in the database
            if bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
                if role == "customer":
                    user = User(role=role, id=user[1], unum=user[2], password=user[3])
                    print(user)
                    login_user(user)
                    return redirect(url_for('home.home', customerID=user.id))
                elif role == "planner":
                    user = User(role=role, id=user[1], unum=user[2], password=user[3])
                    login_user(user)
                    return redirect(url_for('planner.home', plannerID=user.id))
                elif role == "admin":
                    user = User(role=role, id=user[1], unum=user[2], password=user[3])
                    login_user(user)
                    return redirect(url_for('admin.home', adminID=user.id))
                else:
                    flash('Your password is incorrect.')
                    return render_template('auth/login.html')

            else:
                print(f"Password check failed for user: {email}")
                flash('Invalid input, please check your email or password.')
            return render_template('auth/login.html')
        else:
            print(f"No user found matching: {email}")
            flash('These credentials do not match our records.')
        return render_template('auth/login.html')

    return render_template('auth/login.html')


# Logout route
@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect (url_for ('home.home'))





#imports the Flask module
from flask import Flask
#the LoginManager class is used for handling user authentication in Flask applications.
from flask_login import LoginManager
#connect Python with a MySQL database.
import mysql.connector
# imports the connect module from my APP package connects to database
from APP import connect
#contains configuration settings for my application, stored secret key
from config import Config
from datetime import timedelta

#creates an instance of the Flask class for the application. 
app = Flask(__name__)

#loads the configuration settings from the Config class into your Flask application.
app.config.from_object(Config)

dbconn = None
connection = None


# creates an instance of the LoginManager class.
login_manager = LoginManager()
login_manager.init_app(app)

#establishes a connection to the MySQL database using the parameters defined in the connect module. 
#It then returns a cursor object which can be used to execute SQL commands.
def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, \
    database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn

#import various modules from APP folder
from APP import home
from APP import admin
from APP import auth
from APP import customers
from APP import planners


# Blueprint are the 'small portable app' that plug into main app. So the application is more organised.
app.register_blueprint(home.bp)
app.register_blueprint(auth.auth_bp, url_prefix = '/auth')
app.register_blueprint(admin.admin_bp, url_prefix = '/admin')
app.register_blueprint(customers.cust_bp, url_prefix = '/customer')
app.register_blueprint(planners.pl_bp, url_prefix = '/planner')




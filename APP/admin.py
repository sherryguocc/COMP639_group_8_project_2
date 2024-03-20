import calendar
import decimal
import json
from flask import Blueprint, render_template, redirect, url_for, flash, request, make_response, Flask
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from fpdf import FPDF
import bcrypt
import random
import string
import re
import os
from datetime import datetime, timedelta
from .classes.venue_model import Venue
from .classes.admin_class import admin
from .classes.customer_class import Customer
from .classes.planner_class import Planner
from .classes.booking_service_class import BookingService
from .classes.additional_service_model import Menu, Decoration
from .classes.notification_model import Notifications
from .classes.calendar_model import Calendar

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'APP/static'  # upload file route
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # accepted file type

# Create a Blueprint for the admin routes
admin_bp = Blueprint('admin', __name__)

#Admin Home
@admin_bp.route('/home', methods=['GET'])
@login_required
def home():
    try:
        anAdmin = admin.get_admin_info(current_user.id)
        unread_messages_count = get_unread_messages_count(current_user.id)
        # check if the admin user exists
        if anAdmin is None:
            flash ('No user data found!')
            return redirect (url_for('home.home'))
        
    except Exception as e:
        flash (str(e), "An error occured while processing your request.")
        return redirect (url_for('home.home'))
    
    return render_template ('admin/home.html', anAdmin = anAdmin, unread_messages_count=unread_messages_count)


@admin_bp.route('/edit_profile/<int:adminID>', methods=['GET', 'POST'])
@login_required
def edit_profile(adminID):
    msg = ''
    try:
        anAdmin = admin.get_admin_info(current_user.id)
        unread_messages_count = get_unread_messages_count(current_user.id)

        if request.method == 'POST':
            Title = request.form.get('title')
            FirstName = request.form.get('first_name')
            LastName = request.form.get('last_name')
            Email = request.form.get('email')
            Phone = request.form.get('phone')

            if not all([Title, FirstName, LastName, Email]):
                msg = "Please make sure all the required fields are filled out."

            if not Phone:
                Phone = ''

            else:
                if not re.match(r'^[A-Za-z]+$', FirstName) or not re.match(r'^[A-Za-z]+$', LastName):
                    msg = "Name should only consist of letters."
                elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', Email):
                    msg = "Invalid email format"
                elif not re.match(r'^\d+$', Phone):
                    msg = "Invalid phone format"
                elif len(Phone) > 15:
                    msg = "The phone number is too long. Please check and re-enter."

            if not msg:
                FirstName = FirstName.title()
                LastName = LastName.title()

                admin.update_admin_profile(Title, FirstName, LastName, Phone, Email, adminID)

                msg = 'Great! Your profile has been updated.'
                return redirect(url_for('admin.home', anAdmin=anAdmin, adminID=adminID, msg=msg))

        elif request.method == 'POST':   # This condition seems redundant, as the previous block already checks for 'POST'.
            msg = "Please make sure all the required fields are filled out."

    except Exception as e:
        flash(str(e), "An error occurred while processing your request.")
        return redirect(url_for('home.home'))

    return render_template('admin/edit_profile.html', adminID=adminID, anAdmin=anAdmin, msg=msg, unread_messages_count=unread_messages_count)


def is_valid_password(password):
    # check password length
    if len(password) < 8:
        return False
    # check password format
    if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)', password):
        return False
    return True

# Route to allow admin to change password
@admin_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    msg = ''
    adminID = current_user.id
    anAdmin = admin.get_admin_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)

    if request.method == 'POST':
        if not all(request.form.get(field) for field in ['old_password', 'new_password', 'confirm_new_password']):
            msg = 'Please fill out all the fields.'
        else:
            old_password = request.form.get('old_password')
            new_password = request.form.get('new_password')
            confirm_new_password = request.form.get('confirm_new_password')
            current_password_hash = anAdmin[8]

            if bcrypt.checkpw(old_password.encode('utf-8'), current_password_hash.encode('utf-8')):
                if not is_valid_password(new_password):
                    msg = 'Password must be at least 8 digits with both letters and numbers.'
                elif confirm_new_password == new_password:
                    hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                    admin.update_admin_password(hashed_new_password, adminID)
                    flash('Password updated successfully!')
                    return render_template('admin/home.html', adminID=adminID, anAdmin=anAdmin, msg=msg, unread_messages_count=unread_messages_count)
                else:
                    msg = 'Please confirm, the new passwords do not match'
            else:
                msg = 'Your old password is incorrect'

    return render_template('admin/change_password.html', msg=msg, anAdmin=anAdmin, unread_messages_count=unread_messages_count)

@admin_bp.route('/customer_list', methods=['GET','POST'])
@login_required
def view_customer():
    msg = ''
    anAdmin = admin.get_admin_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    customer_list = Customer.get_all_cust()
    if request.method == 'POST':
        if 'search_customer' in request.form:
            search_customer = request.form.get('search_customer')
            customer_list = Customer.search_customer(search_customer)
            return render_template('/admin/customer_list.html', customer_list = customer_list, anAdmin = anAdmin, msg = msg, unread_messages_count=unread_messages_count)
        
        elif 'btn_register' in request.form:
            title = request.form.get('title')
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            email = request.form.get('email')
            password = request.form.get('password')
            if not is_valid_password(password):
                msg = 'Password must be at least 8 digit with both letters and numbers.'
                return render_template('/admin/customer_list.html', anAdmin=anAdmin, msg=msg, customer_list = customer_list, unread_messages_count=unread_messages_count)
            else:
                existing_email = Customer.get_customer_by_email(email)

            if existing_email is not None:
                if existing_email:
                    msg = 'Duplicate Email.'
                return render_template('/admin/customer_list.html', anAdmin=anAdmin, msg=msg, customer_list = customer_list, unread_messages_count=unread_messages_count)
            else:
                hashedp = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                user_no = "c" + ''.join(random.choices(string.digits, k = 5))

                admin.add_customer(user_no, title, first_name, last_name, email, hashedp)
                msg = 'New user added.'
            return render_template('/admin/customer_list.html', customer_list = customer_list, anAdmin = anAdmin, msg = msg, unread_messages_count=unread_messages_count)
    return render_template('/admin/customer_list.html', customer_list = customer_list, anAdmin = anAdmin, unread_messages_count=unread_messages_count)
    
@admin_bp.route('/manage_customer/<int:custID>', methods=['GET','POST'])
@login_required
def manage_customer(custID):
    msg = ''
    anAdmin = admin.get_admin_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    aCust = Customer.get_cust_info(custID)
    aCust_ID = aCust[0]
    print(f"Accessing manage_customer route with custID: {aCust_ID}")
    if request.method == 'POST':
        if request.form.get('delete_cust'):
            print("Delete customer branch entered")
            customer_id = request.form.get('delete_cust')
            admin.delete_customer(custID)
            customer_list = Customer.get_all_cust()
            msg = 'This customer has been deleted.'
            return redirect(url_for('admin.view_customer', anAdmin=anAdmin, msg=msg, customer_list=customer_list, aCust = aCust, aCust_ID = aCust_ID))
        
        elif request.form.get('btn_message'):
            print("Sending message branch entered")
            customer_id = request.form.get('customer_id')
            message_date = request.form.get('message_date')
            message = request.form.get('message')
            message_image = request.form.get('message_image')

            message_date = request.form.get('message_date')
            if not message_date:
                message_date = datetime.now().strftime('%Y-%m-%d')

            admin.admin_send_message_cust(customer_id, message_date, message, message_image, current_user.id)
            flash('Message has been sent.') 
            return redirect(url_for('admin.manage_customer', custID=aCust_ID, customer_selected=aCust, anAdmin=anAdmin))

        else:
            print("Updating customer profile branch entered")
            title = request.form.get('title')
            firstName = request.form.get('first_name')
            lastName = request.form.get('last_name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            address = request.form.get('address')
            dob = request.form.get('dob')
            print(f"Received values - Title: {title}, First Name: {firstName}, Last Name: {lastName}, email: {email}, phone: {phone}, address: {address}, dob: {dob}") 
            if not phone:
                phone = None
            
            if not address:
                address = None
            
            if not dob:
                dob = None
            admin.update_customer_profile(title, firstName, lastName, phone, email, address, dob, custID)
            flash ('The details of the customer have been updated.') 
            return redirect(url_for('admin.view_customer', customer_selected = aCust, anAdmin = anAdmin, aCust = aCust, aCust_ID = aCust_ID))
    return render_template('/admin/manage_customer.html', customer_selected = aCust, aCust_ID = aCust_ID, anAdmin = anAdmin, aCust = aCust, msg = msg, unread_messages_count=unread_messages_count)


def is_valid_password(password):
    if len(password) < 8:
        return False
    if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)', password):
        return False
    return True

@admin_bp.route('/planner_list', methods=['GET','POST'])
@login_required
def view_planner():
    msg = ''
    anAdmin = admin.get_admin_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    planner_list = Planner.get_all_planners()
    if request.method == 'POST':
        if 'search_planner' in request.form:
            search_planner = request.form.get('search_planner')
            planner_list = Planner.search_planner(search_planner)
            return render_template('/admin/planner_list.html', planner_list = planner_list, anAdmin = anAdmin, msg = msg, unread_messages_count=unread_messages_count)
        
        elif 'btn_register' in request.form:
            title = request.form.get('title')
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            email = request.form.get('email')
            password = request.form.get('password')
            if not is_valid_password(password):
                msg = 'Password must be at least 8 digit with both letters and numbers.'
                return render_template('/admin/planner_list.html', anAdmin=anAdmin, msg=msg, planner_list = planner_list, unread_messages_count=unread_messages_count)
            else:
                existing_email = Planner.get_planner_by_email(email)

            if existing_email is not None:
                msg = 'Duplicate Email.'
                return render_template('/admin/planner_list.html', anAdmin=anAdmin, msg=msg, planner_list = planner_list, unread_messages_count=unread_messages_count)
            else:
                hashedp = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                user_no = "p" + ''.join(random.choices(string.digits, k = 5))

                admin.add_planner(user_no, title, first_name, last_name, email, hashedp)
                flash('New user added.')
            return redirect(url_for('admin.view_planner', planner_list = planner_list, anAdmin = anAdmin))
    return render_template('/admin/planner_list.html', planner_list = planner_list, anAdmin = anAdmin, unread_messages_count=unread_messages_count)


@admin_bp.route('/manage_planner/<int:plannerID>', methods=['GET','POST'])
@login_required
def manage_planner(plannerID):
    msg = ''
    anAdmin = admin.get_admin_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    planner_selected = Planner.get_plan_info(plannerID)
    print(planner_selected)
    plannerID = planner_selected[0]
    print(plannerID)
    if request.method == 'POST':
        if request.form.get('delete_plan'):
            planner_id = request.form.get('delete_plan')
            admin.delete_planner_by_id(planner_id)
            planner_list = Planner.get_all_planners()
            msg = 'This planner has been deleted.'
            return redirect (url_for('admin.view_planner', planner_list = planner_list))
        else:
            title = request.form.get('title')
            firstName = request.form.get('first_name')
            lastName = request.form.get('last_name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            address = request.form.get('address')
            profile = request.form.get('profile')
            profile_pic = request.form.get('profile_pic')
            
            admin.update_planner(title, firstName, lastName, phone, email, address, profile, profile_pic, planner_selected[0])
            msg = 'The details of the planner have been updated.' 
            return redirect (url_for('admin.view_planner'))

    return render_template('/admin/manage_planner.html', planner_selected=planner_selected, plannerID=plannerID, anAdmin=anAdmin, msg=msg, unread_messages_count=unread_messages_count)



# US: As an admin,  I want to be able to view all the bookings,  So that I can be aware of the bookings customer made. 
""" AC:
1. Access 'Booking' from the main dashboard. 
2. An interface displays a list of all bookings both current and historic. 
3. There is a clear distinction or section where past (historic) bookings are listed. 
4. Each booking entry shows key details such as customer name, venue, date & time, and event type. 
5. Each booking has a status indicator, such as confirmed, pending, cancelled, or completed. 
6. Upon selecting a specific booking, the Admin can view detailed information including customer contact details, special requests or notes, payment status, and any associated planners or staff.  """


@admin_bp.route('/view_bookings', methods=['GET', 'POST'])
@login_required
def view_bookings():
    # get admin details
    anAdmin = admin.get_admin_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    historic_bookings = []
    current_bookings = []
    try:
        # get history bookings
        historic_bookings = admin.view_historic_bookings()
        #get current bookings
        current_bookings = admin.view_current_bookings() 

        # if search feature is used
        if request.method == 'POST':
            keyword = request.form['keyword']

            if keyword:
                likekeyword = f'%{keyword}%'
                # get the searched booking results by keyword
                historic_bookings = admin.search_history_bookings(likekeyword)
                current_bookings = admin.search_current_bookings(likekeyword)
                return render_template ('admin/view_all_bookings.html', anAdmin = anAdmin, historic_bookings = historic_bookings, unread_messages_count=unread_messages_count, current_bookings = current_bookings)
            else:
                flash('Please enter a keyword')
                
    except Exception as e:
        flash(str(e), "An error occurred while processing your request.")
        print(f"Error: {e}")  
    return render_template ('admin/view_all_bookings.html', anAdmin = anAdmin, historic_bookings = historic_bookings, unread_messages_count=unread_messages_count, current_bookings = current_bookings)


# get a booking deatils by booking id
def get_booking_by_id(booking_id):
    a_booking = BookingService.admin_check_booking_details(booking_id)
    return a_booking

@admin_bp.route('individual_booking_details/<int:booking_id>', methods = ['GET', 'POST'])
@login_required
def individual_booking_details(booking_id): 
    # get admin details
    anAdmin = admin.get_admin_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    print(f"Admin Info: {anAdmin}") 
    try:
        # get a booking details
        booking = get_booking_by_id(booking_id)
        print(f"Booking Details: {booking}") # Debugging statement 4
        # create a booking details PDF
        if request.method == 'POST':
            print("POST request received.") # Debugging statement 5
            
            if 'export_method' in request.form:
                response = generate_booking_pdf(booking_id)
                print(f"Generating booking PDF for booking_id: {booking_id}") # Debugging statement 6
                return response

    except Exception as e:
        flash(str(e), "An error occurred while processing your request.")
        print(f"Error encountered: {e}")  # Debugging statement 7
        return redirect(url_for('admin.view_bookings'))
    
    print("Rendering individual_booking_details.html template.") # Debugging statement 8
    return render_template('admin/individual_booking_details.html', booking = booking, anAdmin = anAdmin, booking_id = booking_id, unread_messages_count=unread_messages_count)



class PDFWithFooter(FPDF):
    def __init__(self, admin_id):
        self.admin_id = admin_id  
        super().__init__()

    def footer(self):
        # Get admin info
        anAdmin = admin.get_admin_info(self.admin_id)
        # add footer content
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, -20, "Plan It Right Event Management Co.", align='C', ln=True)
        self.cell(0, 10, txt=f"Admin: {anAdmin[1]} - {anAdmin[3]} {anAdmin[4]}", align='C')


def generate_booking_pdf(booking_id):
    booking = get_booking_by_id(booking_id)  # Fetch the bookings from the database
    
    admin_id = current_user.id

    # create PDF footer
    pdf = PDFWithFooter(admin_id)

    # create a new page
    pdf.add_page()

    # add a logo
    pdf.image("APP\static\Plan-ItRight.jpg", x=10, y=10, w=50, h=50)

    # title
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 60, txt="Booking Details", ln=True, align='C')

    # subtitle
    pdf.set_font("Arial", size=8)
    pdf.cell(200, -40, txt=f"Booking ID: {booking[0]} | | Booking Status: {booking[16]}", ln=True, align='C')
    
    # create a Event Details column
    pdf.set_fill_color(227, 218, 225) # set background colour
    pdf.rect(10, 60, 190, 10, 'F')   # create a rectangle
    pdf.set_text_color(0, 0, 0)  # set text color as black
    pdf.set_font("Arial", size=13)
    pdf.cell(200, 70, txt="Event Details", ln=True, align='C')
    
    pdf.set_font("Arial", size=10)
    pdf.cell(20, -50, txt=f"Booking Start Date and Time: {booking[11].strftime('%d-%m-%Y')} {booking[12]}", ln=True)
    pdf.cell(20, 60, txt=f"Booking End Date and Time: {booking[13].strftime('%d-%m-%Y')} {booking[14]}", ln=True)
    pdf.cell(20, -50, txt=f"Venue Name: {booking[7]}", ln=True)
    pdf.cell(20, 60, txt=f"Venue Location: {booking[8]}", ln=True)
    pdf.cell(20, -50, txt=f"Guest Number: {booking[15]}", ln=True)
    
    # create a Additional Service column
    pdf.set_fill_color(227, 218, 225)  
    pdf.rect(10, 100, 190, 10, 'F') 
    pdf.set_text_color(0, 0, 0)  
    pdf.set_font("Arial", size=13)
    pdf.cell(200, 70, txt="Additional Service", ln=True, align='C')
    
    pdf.set_font("Arial", size=10)
    pdf.cell(20, -50, txt=f"Food Order: {booking[9] or 'N/A'}", ln=True)
    pdf.cell(20, 60, txt=f"Decoration Order: {booking[10] or 'N/A'}", ln=True)

    # create a Planner Details column
    pdf.set_fill_color(227, 218, 225)  
    pdf.rect(10, 130, 190, 10, 'F')  
    pdf.set_text_color(0, 0, 0)  
    pdf.set_font("Arial", size=13)
    pdf.cell(200, -30, txt="Planner Details", ln=True, align='C')
    
    pdf.set_font("Arial", size=10)
    pdf.cell(20, 50, txt=f"Planner Name: {booking[3]} - {booking[4]}", ln=True)
    pdf.cell(20, -40, txt=f"Phone Number: {booking[6] or 'N/A'}", ln=True)
    pdf.cell(20, 50, txt=f"Email Address: {booking[5] or 'N/A'}", ln=True)

    # create a Customer Details column
    pdf.set_fill_color(227, 218, 225)  
    pdf.rect(10, 160, 190, 10, 'F')  
    pdf.set_text_color(0, 0, 0)  
    pdf.set_font("Arial", size=13)
    pdf.cell(200, -30, txt="Customer Details", ln=True, align='C')
    
    pdf.set_font("Arial", size=10)
    pdf.cell(20, 50, txt=f"Customer Name: {booking[1]} - {booking[2] or 'N/A'}", ln=True)
    pdf.cell(20, -40, txt=f"Phone Number: {booking[17] or 'N/A'}", ln=True)
    pdf.cell(20, 50, txt=f"Email Address: {booking[18] or 'N/A'}", ln=True)
    
    # create a Comments column
    pdf.set_fill_color(227, 218, 225)  
    pdf.rect(10,190, 190, 10, 'F')  
    pdf.set_text_color(0, 0, 0)  
    pdf.set_font("Arial", size=13)
    pdf.cell(200, -30, txt="Comments", ln=True, align='C')

    pdf.set_font("Arial", size=10)
    pdf.cell(20, 50, txt=f"{booking[19] or 'N/A'}", ln=True)
    
    
    # Add a line to separate bookings
    pdf.ln(10)

    response  = make_response(pdf.output(dest='S').encode('latin1'))
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"inline; filename=Booking_No{booking[0]}.pdf"
    return response

# Route for viewing the list of venues in the admin dashboard
@admin_bp.route('/venue_list')
def venue_list():
    anAdmin = admin.get_admin_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)

    # get fileter index
    sort_column = request.args.get('sort_column', 'default_column')
    sort_direction = request.args.get('sort_direction', 'asc')
    # Get the list of venues from the Venue model
    venueList = Venue.get_venue_list()

    # sorted the list by filter index
    venueList = Venue.sort_venue_list(venueList, sort_column, sort_direction)
    # sorted the list by type
    selected_type = request.args.get('type', 'all')
    venueList = Venue.sort_venueList_by_type(venueList, selected_type)
    # sorted the list by status
    selected_status = request.args.get('status', 'all')
    venueList = Venue.sort_venueList_by_status(venueList, selected_status)
    
    # Paginate the venue list
    page = request.args.get('page', 1, type=int)
    per_page = 6

    # Paginate the venue list
    start_index = (page - 1) * per_page
    end_index = start_index + per_page

    paginated_venues = venueList[start_index:end_index]


    return render_template('admin/venue_list.html', 
                           anAdmin=anAdmin, 
                           venueList=paginated_venues, 
                           page=page, 
                           per_page=per_page, 
                           sort_column=sort_column, 
                           sort_direction=sort_direction, 
                           selected_type=selected_type, 
                           selected_status=selected_status, 
                           unread_messages_count=unread_messages_count)



# Route for adding a new venue page
@admin_bp.route('/add_venue', methods=['GET', 'POST'])
def add_venue():
    anAdmin = admin.get_admin_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    if request.method == 'POST':
        # Retrieve form data for adding a new venue
        venue_name = request.form['venue_name']
        event_area = float(request.form['event_area'])
        max_capacity = int(request.form['max_capacity'])
        location = request.form['location']
        status = request.form['status']
        daily_price = float(request.form['daily_price'])
        hourly_price = float(request.form['hourly_price'])
        selected_types = request.form.getlist('type')
        venue_type = ', '.join(selected_types)
        description = request.form['description']
        rented = 0

        # Process image input information and convert it into JSON
        image_urls_text = request.form['image_urls']
        image_urls_json = Venue.process_image_urls_to_json(image_urls_text)

        # Handle optional fields
        if not daily_price:
            daily_price = None
        if not hourly_price:
            hourly_price = None
        if not description:
            description = None
        if not rented:
            rented = None
        if not venue_type:
            venue_type = None

        new_venue = Venue(None, venue_name, event_area, max_capacity, location, status, daily_price, hourly_price, description, rented, image_urls_json, venue_type)
        result = Venue.add_venue(new_venue)
        
        if result:
            flash('Venue added successfully!', 'success')

        flash('Venue added successfully!', 'success')

        return redirect(url_for('admin.venue_list', anAdmin=anAdmin))

    return render_template('admin/add_venue.html', anAdmin = anAdmin, unread_messages_count=unread_messages_count)

# Route for changing the status of a venue
@admin_bp.route('/change_venue_status/<int:venue_id>', methods=['POST'])
def change_venue_status(venue_id):
    venue = Venue.get_venue_by_id(venue_id)
    anAdmin = admin.get_admin_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    if venue:
        if venue.is_active:
            venue.status = False
        else:
            venue.status = True

        venue.update_to_database()
        flash('Venue status changed successfully!', 'success')
    else:
        flash('Venue not found!', 'error')

    return redirect(url_for('admin.venue_list', anAdmin=anAdmin))

# Route for editing a venue
@admin_bp.route('/edit_venue/<int:venue_id>', methods=['GET', 'POST'])
def edit_venue(venue_id):
    anAdmin = admin.get_admin_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    venue_info = Venue.get_venue_by_id(venue_id)
    if request.method == 'GET':
        return render_template('admin/edit_venue.html', venue_info=venue_info, anAdmin=anAdmin, unread_messages_count=unread_messages_count)
    if request.method == 'POST':
        # Update venue's information in the database
        venue_name = request.form['venue_name']
        event_area = float(request.form['event_area'])
        max_capacity = int(request.form['max_capacity'])
        location = request.form['location']
        daily_price = float(request.form['daily_price'])
        hourly_price = float(request.form['hourly_price'])
        description = request.form['description']
        venue_type = request.form['type']
        rented = 0

        # Check whether there is a change in any attribute
        attributes_to_update = {
            'venueName': venue_name,
            'eventArea': event_area,
            'maxCapacity': max_capacity,
            'location': location,
            'dailyPrice': daily_price,
            'hourlyPrice': hourly_price,
            'description': description,
            'rented': rented,
            'type': venue_type
        }
        for attribute, new_value in attributes_to_update.items():
            if new_value != getattr(venue_info, f'get_{attribute}'):
                setattr(venue_info, attribute, new_value)

        venue_info.update_to_database()

        flash('Venue information updated successfully!', 'success')
        return redirect(url_for('admin.edit_venue', venue_id=venue_info.get_venueID, anAdmin=anAdmin))

# Route for deleting an image associated with a venue
@admin_bp.route('/delete_image/<int:venue_id>', methods=['POST'])
def delete_image(venue_id):
    data = request.get_json()
    image_url_to_delete = data['image_url']
    venue = Venue.get_venue_by_id(venue_id)
    if venue:
        venue.delete_image(image_url_to_delete)
        return 'Image deleted successfully', 200
    else:
        return 'Venue not found', 404

# Route for adding an image to a venue
@admin_bp.route('/add_image/<int:venue_id>', methods=['POST'])
def add_image(venue_id):
    anAdmin = admin.get_admin_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    venue = Venue.get_venue_by_id(venue_id)
    image_urls_text = request.form['image_urls_text']
    if venue and image_urls_text:
        venue.add_image(image_urls_text)
        flash('Image added successfully', 'success')
    else:
        flash('Venue not found or missing image URLs', 'error')

    return redirect(url_for('admin.edit_venue', venue_id=venue_id, anAdmin = anAdmin,  unread_messages_count =  unread_messages_count))

# Route for deleting a specific venue
@admin_bp.route('/delete_venue/<int:venue_id>', methods=['GET', 'POST'])
def admin_delete_venue(venue_id):
    anAdmin = admin.get_admin_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    venue_info = Venue.get_venue_by_id(venue_id)
    if venue_info:
        venue_info.delete_venue()
        flash('Venue deleted successfully!', 'success')
        return redirect(url_for('admin.venue_list', anAdmin=anAdmin,  unread_messages_count =  unread_messages_count))
    else:
        flash('Venue not found!', 'error')
        return redirect(url_for('admin.venue_list', anAdmin=anAdmin,  unread_messages_count =  unread_messages_count))
    
    

# As an admin,I want to be able to assign a planner to a booking, So that I can make a specific planner responsible for a certain booking.
"""Acceptance Criteria:
•Each booking provides an "Assign" button.
•Upon selecting "Assign", admin can choose a planner to be in charge of this booking.
•To change in charge planner, admin can also use this button to do the assign again.
•After assigned this booking, a success information will show on screen with the assigned information: booking is assigned to the planner XXX.
•Each time the assign function successfully finished, planner and customer will receive notifications."""
# Route for planner to see all the unassigned bookings
@admin_bp.route('/unassign_bookings')
@login_required
def unassign_bookings():
    anAdmin =  admin.get_admin_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    today = datetime.now().date()
    try:
        unassigned_bookings = BookingService.planner_view_available_bookings(today)
    except Exception as e:
        flash(str(e), "An error occured while processing your request.")
    return render_template('admin/unassigned_bookings.html', unassigned_bookings = unassigned_bookings, anAdmin=anAdmin, unread_messages_count=unread_messages_count)

# assign/reassign a booking to a planner
@admin_bp.route('/assign_booking/<int:booking_id>', methods=['GET','POST'])
@login_required
def assign_booking(booking_id):
    anAdmin = admin.get_admin_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    today = datetime.now().date()
    try:
        planner_current_booking_number = BookingService.planner_current_booking_number()
        
        if request.method == 'POST':
            # Search a planner
            if 'search_planner' in request.form:
                keyword = request.form.get('search_planner')
                likekeyword = f'%{keyword}%'
                planner_current_booking_number = BookingService.search_planner_current_booking_number(likekeyword)
                return render_template('admin/assign_booking.html', anAdmin = anAdmin, planner_current_booking_number = planner_current_booking_number, unread_messages_count=unread_messages_count, booking_id=booking_id)
            
            # Assign this booking to a planner
            elif 'planner_id' in request.form:
                planner_id = request.form.get('planner_id')
                booking=BookingService.get_booking_by_id(booking_id)

                # If this booking already has a planner
                if booking[16]:
                    BookingService.planner_accept_booking(planner_id, booking_id)
                    booking=BookingService.get_booking_by_id(booking_id)

                    today = datetime.today().date()
                    NZ_formatted_date = today.strftime("%d-%m-%Y")

                    # Send messages aabout the changing to customer and planner
                    message_to_customer = f'{NZ_formatted_date} - Hi {booking[20]},Your booking at {booking[18]} has been assigned to a new planner {booking[19]}. -- From Admin {anAdmin[3]} {anAdmin[4]}'
                    message_to_planner = f'{NZ_formatted_date} - Hi {booking[19]}, you have been assigned a new job at {booking[18]}, please check your bookings. -- From Admin {anAdmin[3]} {anAdmin[4]}'

                    today = datetime.today().date()
                    print(f"today: {today}, customerID: {booking[14]}, current user id: {current_user.id}, message: {message_to_customer}")

                    BookingService.admin_insert_reminder_to_customer(today, booking[14], message_to_customer)
                    BookingService.admin_insert_reminder_to_planner(today, planner_id, message_to_planner)

                    msg = f"Booking {booking[15]} has been re-assigned to planner {booking[16]} - {booking[19]}"
                    return redirect(url_for('admin.view_bookings', msg = msg))
                
                # If this booking does not have a planner
                elif booking[16] == None:
                    BookingService.planner_accept_booking(planner_id, booking_id)
                    # flash('The booking has been assigned to planner')
                    
                    booking=BookingService.get_booking_by_id(booking_id)

                    today = datetime.today().date()
                    NZ_formatted_date = today.strftime("%d-%m-%Y")

                    # Send message to customer and planner
                    message_to_customer = f'{NZ_formatted_date} - Hi {booking[20]},Your booking at {booking[18]} has been assigned to planner {booking[19]}. -- From Admin {anAdmin[3]} {anAdmin[4]}'
                    print(message_to_customer)

                    message_to_planner = f'{NZ_formatted_date} - Hi {booking[19]}, you have been assigned a new job at {booking[18]}, please check your bookings. -- From Admin {anAdmin[3]} {anAdmin[4]}'

                    
                    print(f"today: {today}, customerID: {booking[14]}, current user id: {current_user.id}, message: {message_to_customer}")

                    BookingService.admin_insert_reminder_to_customer(today, booking[14], message_to_customer)
                    BookingService.admin_insert_reminder_to_planner(today, planner_id, message_to_planner)

                    msg = f"Great! This booking has been assigned to planner {booking[16]} - {booking[19]}"

                    unassigned_bookings = BookingService.planner_view_available_bookings(today)
                    return render_template('admin/unassigned_bookings.html', unassigned_bookings = unassigned_bookings, anAdmin=anAdmin, msg=msg, unread_messages_count=unread_messages_count)

        return render_template('admin/assign_booking.html', anAdmin = anAdmin, planner_current_booking_number = planner_current_booking_number, booking_id=booking_id, unread_messages_count=unread_messages_count)
    except Exception as e:
        msg = str(e), "An error occured while processing your request."
        return msg


#As an admin,I want to be able to cancel a booking,So that I can help customers to cancel a booking if they can’t do it by themselves.
""" AC:
•Each booking provides a "Cancel" option.
•Upon selecting "Cancel", a confirmation prompt appears to ensure the Admin intends to cancel the booking.
•If confirmed, the booking status changes to "Cancelled”.
•A system notification or alert can be sent to the associated customer or planner about the cancellation."""
# assign a booking to a planner
@admin_bp.route('/delete_booking/<int:booking_id>', methods=['GET','POST'])
@login_required
def cancel_booking(booking_id):
    anAdmin = admin.get_admin_info(current_user.id)
    # unread_messages_count = get_unread_messages_count(current_user.id)
    try:
        BookingService.cancel_booking(booking_id)
        Calendar.delete_calendar_due_to_booking(booking_id)
        # Calendar.delete_calendar_entry(booking_id)
        
        booking=BookingService.get_booking_by_id(booking_id)
        today = datetime.today().date()
        NZ_formatted_date = today.strftime("%d-%m-%Y")
        # Send message to customer and planner
        message_to_customer = f'{NZ_formatted_date} - Hi {booking[20]}, your booking at {booking[18]} has been cancelled. If you have any questions please feel free to contact us. -- From Admin {anAdmin[3]} {anAdmin[4]}'
        print(message_to_customer)

        message_to_planner = f'Hi {booking[19]}, your job at {booking[18]} has been cancelled, please check your bookings. -- From Admin {anAdmin[3]} {anAdmin[4]}'

        
        print(f"today: {today}, customerID: {booking[14]}, current user id: {current_user.id}, message: {message_to_customer}")

        BookingService.admin_insert_reminder_to_customer(today, booking[14], message_to_customer)
        BookingService.admin_insert_reminder_to_planner(today, booking[16], message_to_planner)

        flash("This booking has been cancelled.")
        return redirect(url_for('admin.view_bookings', anAdmin=anAdmin))

    except Exception as e:
        msg = str(e), "An error occured while processing your request."
        return msg

@admin_bp.route('/menu_list')
def menu_list():
    unread_messages_count = get_unread_messages_count(current_user.id)
    #get the index for sorting menu List
    sort = request.args.get('sort') 
    menuList = Menu.get_menu_list()
    # sort menu List by different trigger
    if sort:
        sort_parts = sort.split('-')
        if len(sort_parts) == 2:
            sort_column, sort_direction = sort_parts
            menuList = Menu.sort_menu_list(menuList, sort_column, sort_direction)

    anAdmin = admin.get_admin_info(current_user.id)

    return render_template('admin/menu_list.html', menuList=menuList, anAdmin=anAdmin, unread_messages_count=unread_messages_count)

# Route for adding a new menu page
@admin_bp.route('/add_menu', methods=['GET', 'POST'])
def add_menu():
    unread_messages_count = get_unread_messages_count(current_user.id)
    anAdmin = admin.get_admin_info(current_user.id)
    
    if request.method == 'POST':
        # Retrieve form data for adding a new menu
        menu_name = request.form['menu_name']       
        # Check if the menu with the same name exists
        existing_menu = Menu.get_menu_by_name(menu_name)      
        if existing_menu:
            flash('Menu with this name already exists. Please choose a different name.', 'error')
            return render_template('admin/add_menu.html', anAdmin=anAdmin, unread_messages_count=unread_messages_count)
        
        price = float(request.form['price'])
        description = request.form['description']

        # upload the image file and return the image name
        menu_image_name = upload_menu_image(app, menu_name)
        
        #if upload successfully then add this menu into database
        if menu_image_name:
            try:
                # Attempt to create a new menu with the provided price
                new_menu = Menu(None, menu_name, price, menu_image_name, description)
                Menu.add_menu(new_menu)
            
                flash('Menu added successfully!', 'success')
                return redirect(url_for('admin.menu_list', anAdmin=anAdmin))
            
            except ValueError as e:
                flash(str(e), 'error')  # Handle validation error
                return render_template('admin/add_menu.html', anAdmin=anAdmin, unread_messages_count=unread_messages_count)
        
    return render_template('admin/add_menu.html', anAdmin=anAdmin, unread_messages_count=unread_messages_count)

def upload_menu_image(app, menu_name):
    if 'menu_image' in request.files:
        menu_image = request.files['menu_image']
        if menu_image.filename != '':
            # Get the file extension
            file_extension = os.path.splitext(menu_image.filename)[1].lower()

            # Define a set of allowed file extensions
            allowed_extensions = {'jpg', 'jpeg', 'png', 'gif'}

            if file_extension[1:] not in allowed_extensions:
                flash('Invalid file format. Supported formats: jpg, jpeg, png, gif', 'error')
            else:
                # Ensure the folder exists
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

                # Combine menu_name with the original file extension
                filename = f"{secure_filename(menu_name)}{file_extension}"

                # Save the menu_image file to the folder
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                menu_image.save(file_path)
                print(f"File saved as: {filename}")

                # Return the file object, not just the name
                return filename  # Return the image name to update database
        else:
            flash('No selected file', 'error')
    
    return None


# Route for editing a menu
@admin_bp.route('/edit_menu/<int:menu_id>', methods=['GET', 'POST'])
def edit_menu(menu_id):
    unread_messages_count = get_unread_messages_count(current_user.id)
    anAdmin = admin.get_admin_info(current_user.id)
    menu = Menu.get_menu_by_id(menu_id)
    if request.method == 'GET':
        return render_template('admin/edit_menu.html', menu=menu, menu_id=menu_id, anAdmin=anAdmin, unread_messages_count=unread_messages_count)
    if request.method == 'POST':
        # Update menu's information in the database
        name = request.form['menu_name']
        price = float(request.form['price'])
        description = request.form['description']

        # Check whether there is a change in any attribute
        attributes_to_update = {
            'name': name,
            'price': price,
            'description': description,
        }
        for attribute, new_value in attributes_to_update.items():
            if new_value != getattr(menu, f'{attribute}'):
                setattr(menu, attribute, new_value)

        menu.update_to_database()

        flash('menu information updated successfully!', 'success')
        return redirect(url_for('admin.edit_menu', menu_id=menu_id, anAdmin=anAdmin))

# Route for deleting a specific menu
@admin_bp.route('/delete_menu/<int:menu_id>', methods=['GET', 'POST'])
def delete_menu(menu_id):
    unread_messages_count = get_unread_messages_count(current_user.id)
    anAdmin = admin.get_admin_info(current_user.id)
    menu = Menu.get_menu_by_id(menu_id)
    if menu:
        # delete from database
        menu.delete_menu()
        # delete image file
        delete_menu_image_file(menu.image)
        flash('menu deleted successfully!', 'success')
        return redirect(url_for('admin.menu_list', anAdmin=anAdmin))
    else:
        flash('menu not found!', 'error')
        return redirect(url_for('admin.menu_list', anAdmin=anAdmin))

def delete_menu_image_file(image_name):
    try:
        if image_name:
            image_path = os.path.join('APP/static', os.path.basename(image_name))
            if os.path.exists(image_path):
                os.remove(image_path)
                return True
    except Exception as e:
        print(f"Error deleting image: {str(e)}")
    return False

@admin_bp.route('/delete_menu_image/<int:menu_id>', methods=['POST'])
def delete_menu_image(menu_id):
    anAdmin = admin.get_admin_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)

    if request.method == 'POST':
        menu = Menu.get_menu_by_id(menu_id)

        if menu is not None:
            # delete file
            delete_menu_image_file(menu.image)
            # delete data
            Menu.delete_image(menu_id)
            flash('Image deleted successfully!', 'success')
        else:
            flash('Menu not found', 'error')

        return redirect(url_for('admin.edit_menu', menu_id=menu_id, anAdmin=anAdmin))

# Route for adding a new menu image
@admin_bp.route('/add_menu_image/<int:menu_id>', methods=['POST'])
def add_menu_image(menu_id):
    anAdmin = admin.get_admin_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    menu = Menu.get_menu_by_id(menu_id)

    if request.method == 'POST':
        # Upload file to folder
        new_image = upload_menu_image(app, menu.name)
        # if upload successfully, then update the database
        if new_image:
            # Update the 'image' attribute of the 'menu' object
            menu.update_image(new_image, menu_id)
            flash('Image upload successfully', 'success')
            return redirect(url_for('admin.edit_menu', menu_id=menu_id, anAdmin=anAdmin))
        
        else:
            flash('Image upload failed', 'error')
            return redirect(url_for('admin.edit_menu', menu_id=menu_id, anAdmin=anAdmin))


@admin_bp.route('/decoration_list')
def decoration_list():
    unread_messages_count = get_unread_messages_count(current_user.id)
    #get the index for sorting decoration List
    sort = request.args.get('sort') 
    decorationList = Decoration.get_decoration_list()
    # sort decoration List by different trigger
    if sort:
        sort_parts = sort.split('-')
        if len(sort_parts) == 2:
            sort_column, sort_direction = sort_parts
            decorationList = Decoration.sort_decoration_list(decorationList, sort_column, sort_direction)

    anAdmin = admin.get_admin_info(current_user.id)

    return render_template('admin/decoration_list.html', decorationList=decorationList, anAdmin=anAdmin, unread_messages_count=unread_messages_count)

# Route for adding a new decoration page
@admin_bp.route('/add_decoration', methods=['GET', 'POST'])
def add_decoration():
    anAdmin = admin.get_admin_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    
    if request.method == 'POST':
        # Retrieve form data for adding a new decoration
        decoration_type = request.form['decoration_type']       
        # Check if the decoration with the same name exists
        existing_decoration = Decoration.get_decoration_by_type(decoration_type)      
        if existing_decoration:
            flash('decoration with this name already exists. Please choose a different name.', 'error')
            return render_template('admin/add_decoration.html', anAdmin=anAdmin, unread_messages_count=unread_messages_count)
        
        price = float(request.form['price'])
        description = request.form['description']
        
        new_decoration = Decoration(None, decoration_type, price, description)
        Decoration.add_decoration(new_decoration)
            
        flash('decoration added successfully!', 'success')
        return redirect(url_for('admin.decoration_list', anAdmin=anAdmin))
        
    return render_template('admin/add_decoration.html', anAdmin=anAdmin, unread_messages_count=unread_messages_count)

# Route for editing a decoration
@admin_bp.route('/edit_decoration/<int:decoration_id>', methods=['GET', 'POST'])
def edit_decoration(decoration_id):
    anAdmin = admin.get_admin_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    decoration = Decoration.get_decoration_by_id(decoration_id)
    if request.method == 'GET':
        return render_template('admin/edit_decoration.html', decoration=decoration, decoration_id=decoration_id, anAdmin=anAdmin, unread_messages_count=unread_messages_count)
    if request.method == 'POST':
        # Update decoration's information in the database
        type = request.form['decoration_type']
        price = float(request.form['price'])
        description = request.form['description']

        # Check whether there is a change in any attribute
        attributes_to_update = {
            'decor_type': type,
            'price': price,
            'description': description,
        }

        for attribute, new_value in attributes_to_update.items():
            old_value = getattr(decoration, f'{attribute}')
            if new_value != old_value:
                setattr(decoration, attribute, new_value)
                if new_value != getattr(decoration, attribute):
                    print("Property set failed.")   
                else:
                    print("Property set successfully.")

        decoration.update_to_database()

        flash('decoration information updated successfully!', 'success')
        return redirect(url_for('admin.edit_decoration', decoration_id=decoration_id, anAdmin=anAdmin))

# Route for deleting a specific decoration
@admin_bp.route('/delete_decoration/<int:decoration_id>', methods=['GET', 'POST'])
def delete_decoration(decoration_id):
    anAdmin = admin.get_admin_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    decoration = Decoration.get_decoration_by_id(decoration_id)
    if decoration:
        # delete from database
        decoration.delete_decoration()

        flash('decoration deleted successfully!', 'success')
        return redirect(url_for('admin.decoration_list', anAdmin=anAdmin, unread_messages_count=unread_messages_count))
    else:
        flash('decoration not found!', 'error')
        return redirect(url_for('admin.decoration_list', anAdmin=anAdmin, unread_messages_count=unread_messages_count))

@admin_bp.route('/book/venue/<int:customerID>', methods=['GET', 'POST'])
@login_required
def book_venue(customerID):
    print(f"Entered book_venue with customerID: {customerID}")

    anAdmin = admin.get_admin_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    # try:
    # Update venue status based on today's date
    BookingService.update_venue_rented_status_based_on_end_date()

    #Fetch all venues available
    venues = Venue.get_venue_list()

    # Fetch all decorations and food menus
    decoration = Decoration.get_all_decorations()
    food_menu = Menu.get_all_menus()
        
    # Fetch default menu
    default_menu_id = 1
    default_menu = Menu.get_image_by_food_id(default_menu_id)

    if request.method == 'POST':
        print("Detected POST request.")

        # Handle the POST request for booking

        # Fetch information about the selected venue by venueID
        venueID = request.form.get('venueID')
        selected_venue = Venue.get_venue_by_id(venueID)

        # Fetch the booking end date for date comparison validation later
        booking_end_date = BookingService.get_booking_end_date_by_venue_id(venueID)
        
        venue = selected_venue.get_venueID

        # Parse date and time inputs from the form
        event_date = request.form.get('startDate')
        event_date_object = datetime.strptime(event_date, '%Y-%m-%d').date()
        event_date_db = event_date_object.strftime('%Y-%m-%d')

        event_time = request.form.get('startTime')
        event_time_object = datetime.strptime(event_time, '%H:%M').time()
        event_time_db = event_time_object.strftime('%H:%M')

        end_date = request.form.get('endDate')
        end_date_object = datetime.strptime(end_date, '%Y-%m-%d').date()
        end_date_db = end_date_object.strftime('%Y-%m-%d')

        end_time = request.form.get('endTime')
        end_time_object = datetime.strptime(end_time, '%H:%M').time()
        end_time_db = end_time_object.strftime('%H:%M')

        #Check if the selected dates are in conflict with admin's block dates.

        if not Calendar.validate_before_booking(venueID, event_date_db, end_date_db):
            flash("The selected slot is unavailable. Please choose a different time.")
            return redirect(url_for('admin.book_venue', customerID=customerID, anAdmin = anAdmin, selected_venue=selected_venue, decoration=decoration, food_menu=food_menu))

        guest_number = request.form.get('guestsNumber')
        event_details = request.form.get('comments')
        status = "Pending"


        # Validation
        if not all([event_date, event_time, end_date, end_time, guest_number]):
            flash("The required fields must be filled in.", 'error')
            return redirect(url_for('admin.book_venue', customerID=customerID, anAdmin = anAdmin, selected_venue=selected_venue, decoration=decoration, food_menu=food_menu))

        if event_date_object < datetime.now().date() or end_date_object < datetime.now().date():
            flash("Please select a future date.")
            return redirect(url_for('admin.book_venue', customerID=customerID, anAdmin = anAdmin, selected_venue=selected_venue, decoration=decoration, food_menu=food_menu))

        if event_date_object > end_date_object:
            print("Invalid! End date must be after start date!")
            flash("Invalid! End date must be after start date!")
            return redirect(url_for('admin.book_venue', customerID=customerID, anAdmin = anAdmin, selected_venue=selected_venue, decoration=decoration, food_menu=food_menu))
        
        if event_date_object == end_time_object:
            if event_time_object > end_time_object:
                print("Invalid! End time must be after start time!")
                flash("Invalid! End time must be after start time!")
                return redirect(url_for('admin.book_venue', customerID=customerID, anAdmin = anAdmin, selected_venue=selected_venue, decoration=decoration, food_menu=food_menu))

        if selected_venue.get_rented == 1 and booking_end_date[0] > datetime.now().date():
            print("This venue is currently on hire. Please choose a different venue.")
            flash("This venue is currently on hire. Please choose a different venue.")
            return redirect(url_for('admin.book_venue', customerID=customerID, anAdmin = anAdmin, selected_venue=selected_venue, decoration=decoration, food_menu=food_menu))
            
        if int(guest_number) > selected_venue.get_maxCapacity:
            print('Sorry, guest number exceeds the maximum capacity of the venue. Please choose a different venue.')
            flash('Sorry, guest number exceeds the maximum capacity of the venue. Please choose a different venue.')
            return redirect(url_for('admin.book_venue', customerID=customerID, anAdmin = anAdmin, selected_venue=selected_venue, decoration=decoration, food_menu=food_menu))

        if not event_details:
            event_details = None

        decoration = request.form.get('decoration')
        food = request.form.get('food')

        print(f"Decoration selected: {decoration}")
        print(f"Food selected: {food}")


        if not decoration:
            decoration = None

        if not food:
            food = None

        if not BookingService.is_venue_available(venueID, event_date_db, end_date_db):
            flash("The venue is already booked for the chosen date")
            return redirect(url_for('admin.home', anAdmin = anAdmin, adminID=current_user.id))
        else:
            print("Venue is available, proceeding with booking...")
            print("Creating booking...")
            print("Generating reference number...")
            if decoration is not None and food is not None:
                # Insert booking with food and decoration
                booking_id = BookingService.create_booking(customerID, event_date_db, event_time_db, end_date_db, end_time_db, guest_number, event_details, status)
                ref_num = BookingService.create_or_get_reference_number(booking_id)
                venueorder_id = BookingService.create_venue_order(venue, booking_id)
                decor_order_id = BookingService.create_decor_order(booking_id, decoration)
                menu_order_id = BookingService.create_menu_order(booking_id, food)
                BookingService.update_booking(booking_id, venueorder_id, menu_order_id, decor_order_id)
                Calendar.insert_booked_calendar(booking_id)
                return redirect (url_for('admin.unassign_bookings', anAdmin = anAdmin))
                
            elif decoration is not None:
                # Insert booking with only decoration
                booking_id = BookingService.create_booking(customerID, event_date_db, event_time_db, end_date_db, end_time_db, guest_number, event_details, status)
                ref_num = BookingService.create_or_get_reference_number(booking_id)
                venueorder_id = BookingService.create_venue_order(venue, booking_id)
                decor_order_id = BookingService.create_decor_order(booking_id, decoration)
                BookingService.update_booking(booking_id=booking_id, venueorder_id=venueorder_id, decor_order_id=decor_order_id)
                Calendar.insert_booked_calendar(booking_id)
                return redirect (url_for('admin.unassign_bookings', anAdmin = anAdmin))
                
            elif food is not None:
                # Insert booking with only food menu
                booking_id = BookingService.create_booking(customerID, event_date_db, event_time_db, end_date_db, end_time_db, guest_number, event_details, status)
                ref_num = BookingService.create_or_get_reference_number(booking_id)
                venueorder_id = BookingService.create_venue_order(venue, booking_id)
                menu_order_id = BookingService.create_menu_order(booking_id, food)
                BookingService.update_booking(booking_id=booking_id, venueorder_id=venueorder_id, menu_order_id=menu_order_id)
                Calendar.insert_booked_calendar(booking_id)
                return redirect (url_for('admin.unassign_bookings', anAdmin = anAdmin))
                
            else:
                # Insert booking with no decoration and no food menu
                booking_id = BookingService.create_booking(customerID, event_date_db, event_time_db, end_date_db, end_time_db, guest_number, event_details, status)
                ref_num = BookingService.create_or_get_reference_number(booking_id)
                venueorder_id = BookingService.create_venue_order(venue, booking_id)
                BookingService.update_booking(booking_id, venueorder_id)
                Calendar.insert_booked_calendar(booking_id)
                return redirect (url_for('admin.unassign_bookings', anAdmin = anAdmin))
                    
    # except Exception as e:
    #     print(f"Exception occurred: {str(e)}")
    #     flash("An error occurred while processing your request.", "error")
    #     return redirect(url_for('admin.home', anAdmin = anAdmin, adminID=current_user.id))
    menus_with_index = [{"index": index, "menu": menu} for index, menu in enumerate(food_menu)]
    
    return render_template('admin/add_booking.html',
                               anAdmin = anAdmin, 
                               venues = venues, 
                               decoration=decoration, 
                               food_menu=food_menu, 
                               default_menu=default_menu,
                               menus=menus_with_index,
                               customerID = customerID, 
                               unread_messages_count=unread_messages_count)

    

"""As an admin, I want to be able to edit a booking, So that I can make sure the booking information are all correct and updated. 
* Upon selecting a specific booking, the Admin edit detailed information including customer contact details, special requests or notes, payment status, and any associated planners or staff. 
* After modifications, there is an option to save changes, and the system updates the booking details immediately. """
@admin_bp.route('/edit_booking/<int:booking_id>', methods=['GET','POST'])
@login_required
def edit_booking(booking_id):
    anAdmin = admin.get_admin_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    # Get the selected booking details
    booking = BookingService.get_booking_by_id(booking_id)
    venue_order_id = booking[24]
    decor_order_id = booking[5]
    menu_order_id = booking[2]
    # Get the booking's start and end time and convert it into proper format
    #Converting time format as apparently HTML does not accept 0:00:00 but 00:00:00 (unsure why missing leading 0 for start time)
    #The zfill(len) method adds zeros (0) at the beginning of the string, until it reaches the specified length which is two in this case.
    booking_start_time = str(booking[9])
    start_time_padded = ':'.join([i.zfill(2) for i in booking_start_time.split(':')])

    booking_end_time = str(booking[11])
    end_time_padded = ':'.join([i.zfill(2) for i in booking_end_time.split(':')])

    # Get all the venue, menu, and decoration lists
    venue_list = Venue.get_venue_list() 
    menu_list = BookingService.get_menu_list()
    decoration_list = BookingService.get_decoration_list()


    if request.method == 'POST':
        venue_id = request.form['venue_id']
        status = request.form['status']
        food_id = request.form['food_id']
        decor_id = request.form.get('decor_id')
        comments = request.form['comments']
        guest = request.form['guest']

        # Get start date and end date
        start_date = request.form['start_date']
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = request.form['end_date']
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')

        # Get start and end time
        start_time = request.form['start_time']
        try:
            start_time_object = datetime.strptime(start_time, '%H:%M').time()
        except ValueError:
            start_time_object = datetime.strptime(start_time, '%H:%M:%S').time()
                # For Times
        start_time_sql = start_time_object.strftime('%H:%M:%S')
        print("Event Start Time:", start_time_object)
        
        end_time = request.form['end_time']
        try:
            end_time_object = datetime.strptime(end_time, '%H:%M').time()
        except ValueError:
            end_time_object = datetime.strptime(end_time, '%H:%M:%S').time()
        end_time_sql = end_time_object.strftime('%H:%M:%S')
        print("Event End Time:", end_time_object)

        
        # Validations
        error_messages = []

        # Validate Email address
        email = request.form['email']
        if len(email) == 0:
            email = booking[23]
            error_messages.append('Email cannot be empty!')
        elif email and (not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)):
            error_messages.append('Invalid email format!')

        # Validate Phone number
        phone = request.form['phone']
        if len(phone) == 0:
            phone=''
        elif phone and not re.match(r'^\d+$', phone):
            error_messages.append("Invalid phone format")
        # validate the length of phone number 
        elif phone and len(str(phone))>15:
            error_messages.append("The phone number is too long. Please check and re-enter.")

        # Validate if the guest number is over the venue's max capacity
        selected_venue = Venue.get_venue_by_id(venue_id)
        if int(guest) > selected_venue.get_maxCapacity:
            error_messages.append("The guest number is over the max capacity of the choosen venue, please select another venue.")

        # Calculate time difference of the booking
        # Covert start and end time as datetime.datetime object, set date as any same day, we only caulculate the time part
        start_datetime = datetime(2023, 1, 1, start_time_object.hour, start_time_object.minute, start_time_object.second)
        end_datetime = datetime(2023, 1, 1, end_time_object.hour, end_time_object.minute, end_time_object.second)

        time_difference = end_datetime - start_datetime
        # Set the minimum time difference is 5 hours
        minimum_time_difference = timedelta(hours=5)

        # Check if Start Date is before today
        today = datetime.today()
        # Validate the selected date
        if start_date_obj <= today:
            error_messages.append("The booking start date cannot be today or in the past.")
        elif end_date_obj < start_date_obj:
            error_messages.append("The end date cannot be before the start date.")    
        elif (start_date_obj == end_date_obj) and (time_difference < minimum_time_difference):
            error_messages.append("Sorry, the booking period cannot be lower than 5 housrs.") 

        # Search if the selected date has been taken by other bookings
        booked_venue_date_time = BookingService.find_booked_venue_date_time_by_bookingID(venue_id, booking_id)
        for booked_venue in booked_venue_date_time:
            booked_start = datetime.strptime(booked_venue[0].strftime('%Y-%m-%d'), '%Y-%m-%d')
            booked_end = datetime.strptime(booked_venue[2].strftime('%Y-%m-%d'), '%Y-%m-%d')
            if (start_date_obj >= booked_start and start_date_obj <= booked_end) or (end_date_obj <= booked_end and end_date_obj >= booked_start):
                error_messages.append("Sorry, this venue has been booked during your booking period.")
        
        # Check if there are any error messages
        if error_messages:
            for message in error_messages:
                flash(message)
            return redirect(url_for('admin.edit_booking', booking_id=booking_id))
        
        # Update modified information 
        else:
            BookingService.edit_booking(start_date, start_time_sql, end_date, end_time_sql, venue_id, status, guest, comments, booking_id, venue_order_id)
            Calendar.delete_calendar_due_to_booking(booking_id)
            Calendar.insert_booked_calendar(booking_id)
            admin.admin_edit_customer_profile(booking[14], phone, email)

            today = datetime.today().date()
            NZ_formatted_date = today.strftime("%d-%m-%Y")
            # Send messages about the updated booking to customer and planner
            message_to_customer = f'{NZ_formatted_date} - Hi {booking[20]}, Your booking at {booking[18]} has been updated. Please feel free to contact us if you have any questions. -- From Admin {anAdmin[3]} {anAdmin[4]}'
            message_to_planner = f'{NZ_formatted_date} - Hi {booking[19]}, Your assigned job at {booking[18]} has some changes, please check your bookings. -- From Admin {anAdmin[3]} {anAdmin[4]}'

            print(f"today: {today}, customerID: {booking[14]}, current user id: {current_user.id}, message: {message_to_customer}")

            BookingService.admin_insert_reminder_to_customer(today, booking[14], message_to_customer)
            BookingService.admin_insert_reminder_to_planner(today, booking[16], message_to_planner)


        # Delete decor order if decoration is selected as None
        if len(decor_id)==4:
            if decor_order_id is not None:
                BookingService.delete_decor_order(booking_id)
        # Update decor order if decoration has changed
        elif decor_order_id and len(decor_id)<3:
            BookingService.update_decor_order(decor_id, booking_id)
        # Create a new decor order if decoration is newly added
        elif (decor_order_id is None) and len(decor_id)<3:
            new_decor_order_id = BookingService.create_decor_order(booking_id, decor_id)
            BookingService.insert_decor_order(booking_id, new_decor_order_id)

        # Delete food order if food is selected as None
        if len(food_id)==4:
            if menu_order_id is not None:
                BookingService.delete_menu_order(booking_id)
        # Update food order if food order has changed
        elif menu_order_id and len(food_id)<3:
            BookingService.update_menu_order(food_id, booking_id)
        # Create a new food order if food is newly added
        elif (menu_order_id is None) and len(food_id)<3:
            new_menu_order_id = BookingService.create_menu_order(booking_id, food_id)
            BookingService.insert_menu_order(booking_id, new_menu_order_id)
        
        flash('This booking has been successfully updated!')
        return redirect(url_for('admin.view_bookings', anAdmin=anAdmin))
        
    return render_template('admin/edit_booking.html', anAdmin = anAdmin, booking_id=booking_id, booking = booking, unread_messages_count=unread_messages_count, venue_list = venue_list, decoration_list=decoration_list, menu_list=menu_list, start_time = start_time_padded, end_time = end_time_padded)

    


@admin_bp.route('/view/messages/<int:adminID>')
@login_required
def view_messages(adminID):
    anAdmin =  admin.get_admin_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    messages = []
    try:
        notifications = Notifications()  
        all_messages = notifications.admin_view_messages(adminID)
        messages = [{
            'reminderID': row[7],
            'date': row[4],
            'notification_type': row[8],
            'content': row[5],  
            'snippet': row[6],
            'status': row[9]
        } for row in all_messages]
    except Exception as e:
        flash(str(e), "An error occurred while processing your request.")
        print(f"Exception occurred: {str(e)}")
        return redirect(url_for('admin.home', anAdmin = anAdmin, error_message=str(e)))  

    return render_template('admin/messagebox.html', anAdmin = anAdmin, messages=messages, unread_messages_count=unread_messages_count)

@admin_bp.route('/delete_message/<int:reminderID>', methods=['POST'])
def delete_message(reminderID):
    try:
        print(f"Deleting message with reminderID: {reminderID}")

        # Create an instance of the Notifications class
        notifications = Notifications()

        # Delete the message with the given reminderID
        deleted = notifications.delete_message(reminderID)
        print('delete')

        return ' ', 204
    except Exception as e:
        print(f"Exception occurred while deleting the message: {str(e)}")
        return str(e), 500

@admin_bp.route('/mark_as_read/<int:reminderID>', methods=['POST'])
def mark_as_read(reminderID):
    try:
        print(f"Marking reminderID: {reminderID} as read")
        
        # Create an instance of the Notifications class
        mark = Notifications()
        
        # Mark the notification with the given reminderID as read
        mark_notifications = mark.mark_as_read(reminderID)
        
        return ' ', 204
    except Exception as e:
        print(f"Exception occurred while marking as read: {str(e)}")
        return str(e), 500


def get_unread_messages_count(adminID):
    try:
        # Get the ID of the currently logged-in customer
        adminID = current_user.id
        
        # Create an instance of the Notifications class
        unread = Notifications()
        
        # Get the count of unread messages for the customer
        unread_count = unread.unread_message_count_admin(adminID)

        return unread_count
    except Exception as e:
        # Handle exceptions and display an error flash message
        flash(str(e), "An error occurred while processing your request.")
        print(f"Exception occurred: {str(e)}")

    


@admin_bp.route('/search/results', methods=['GET', 'POST'])
def search_venue():
    try:
        anAdmin = admin.get_admin_info(current_user.id)
        unread_messages_count = get_unread_messages_count(current_user.id)

        if request.method == 'POST':

            search_query = request.form.get('search_query')
            print(f"Search Query: {search_query}")
            
            venues = Venue.search(search_query)
            print(f"Venues: {venues}") 
            
            if not venues:
                flash('No matching venues found, sorry!')
                return redirect(url_for('admin.venue_list'))

    except Exception as e:
        flash(str(e), "An error occured while processing your request.")
        return redirect (url_for('admin.home'))
    
    return render_template ('admin/search_venue_result.html', 
                            anAdmin = anAdmin,
                            venues = venues, 
                            unread_messages_count=unread_messages_count)

# Route for viewing the calendar of a venue
@admin_bp.route('/calendar/<int:venue_id>', methods=['GET','POST'])
def venue_calendar(venue_id):
    venue = Venue.get_venue_by_id(venue_id)
    anAdmin = admin.get_admin_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    if request.method == 'GET':
        calendar_dict= Calendar.fetch_calendar_data(venue_id)
        unread_messages_count = get_unread_messages_count(current_user.id)
        print(calendar_dict)
        return render_template('admin/calendar.html', venue=venue, calendar_dict=calendar_dict, anAdmin=anAdmin, unread_messages_count=unread_messages_count)
    
    if request.method == 'POST':
        start_date = request.form['start_date']
        start_time = request.form['start_time']+ ':00' 
        end_date = request.form['end_date']
        end_time = request.form['end_time']+ ':00' 
        status = request.form['status']
        booking_id = None

        print("start_date:", start_date)
        print("start_time:", start_time)
        print("end_date:", end_date)
        print("end_time:", end_time)

        # Create a Calendar object and set properties
        new_calendar_entry = Calendar(venue_id, start_date, start_time, end_date, end_time, status, booking_id)

        validation_result = new_calendar_entry.validate_and_insert()

        if validation_result[0]:
            flash(validation_result[1], 'success')
            return redirect(url_for('admin.venue_calendar', venue_id=venue_id, anAdmin=anAdmin))
        else:
            flash(validation_result[1], 'error')
            return redirect(url_for('admin.venue_calendar', venue_id=venue_id, anAdmin=anAdmin))
        
@admin_bp.route('/view_bookings_cust/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def view_bookings_cust(customer_id):
    # get the planer's info
    unread_messages_count = get_unread_messages_count(current_user.id)
    anAdmin = admin.get_admin_info(current_user.id)
    aCust = Customer.get_cust_info(customer_id)
    historic_bookings = []
    current_bookings = []
    try:
        # get history bookings
        historic_bookings = admin.view_historic_bookings_cust(customer_id)
        # get current bookings
        current_bookings = admin.view_current_bookings_cust(customer_id)

        # if search function is used
        if request.method == 'POST':
            keyword = request.form['keyword']
            
            if keyword:
                likekeyword = f'%{keyword}%'
                # fecth the searched booking results matching with keyword
                historic_bookings = admin.search_historic_bookings_cust(customer_id, likekeyword)
                current_bookings = admin.search_current_bookings_cust(customer_id, likekeyword)
                return render_template ('admin/view_bookings_cust.html', aCust = aCust, customer_id = customer_id, anAdmin = anAdmin, historic_bookings = historic_bookings, current_bookings = current_bookings, unread_messages_count = unread_messages_count)

            else:
                flash('Please enter a keyword')
                
    except Exception as e:
        flash(str(e), "An error occurred while processing your request.")
        print(f"Error: {e}")  
    return render_template ('admin/view_bookings_cust.html', aCust = aCust, customer_id = customer_id, anAdmin = anAdmin, historic_bookings = historic_bookings, current_bookings = current_bookings, unread_messages_count = unread_messages_count)

@admin_bp.route('individual_booking_details_cust/<int:booking_id>', methods = ['GET', 'POST'])
@login_required
def individual_booking_details_cust(booking_id):
    unread_messages_count = get_unread_messages_count(current_user.id)
    # get the planner details 
    anAdmin = admin.get_admin_info(current_user.id)
    try:
        # get a certain booking details by booking id
        booking = get_booking_by_id(booking_id)
        payment_details = admin.view_payment_details(booking_id)
       
        # create a PDF for a certain booking
        if request.method == 'POST':
            if 'export_method' in request.form:
                response = generate_booking_pdf(booking_id)
                return response

    except Exception as e:
        flash(str(e), "An error occurred while processing your request.")
        print(f"Error: {e}")
        return redirect(url_for('admin.view_bookings_cust'))

    return render_template('admin/individual_booking_details_cust.html', booking = booking, anAdmin = anAdmin, booking_id = booking_id, payment_details = payment_details, unread_messages_count = unread_messages_count)

@admin_bp.route('/view_bookings_plan/<int:plan_id>', methods=['GET', 'POST'])
@login_required
def view_bookings_plan(plan_id):
    unread_messages_count = get_unread_messages_count(current_user.id)
    # get the planer's info
    anAdmin = admin.get_admin_info(current_user.id)
    aPlan = Planner.get_plan_info(plan_id)
    historic_bookings = []
    current_bookings = []
    try:
        # get history bookings
        historic_bookings = admin.view_historic_bookings_plan(plan_id)
        # get current bookings
        current_bookings = admin.view_current_bookings_plan(plan_id)

        # if search function is used
        if request.method == 'POST':
            keyword = request.form['keyword']
            
            if keyword:
                likekeyword = f'%{keyword}%'
                # fecth the searched booking results matching with keyword
                historic_bookings = admin.search_historic_bookings_plan(plan_id, likekeyword)
                current_bookings = admin.search_current_bookings_plan(plan_id, likekeyword)
                return render_template ('admin/view_bookings_plan.html', aPlan = aPlan, plan_id= plan_id, anAdmin = anAdmin, historic_bookings = historic_bookings, current_bookings = current_bookings, unread_messages_count = unread_messages_count)

            else:
                flash('Please enter a keyword')
                
    except Exception as e:
        flash(str(e), "An error occurred while processing your request.")
        print(f"Error: {e}")  
    return render_template ('admin/view_bookings_plan.html', aPlan = aPlan, plan_id = plan_id, anAdmin = anAdmin, historic_bookings = historic_bookings, current_bookings = current_bookings, unread_messages_count = unread_messages_count)
    

def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

def generate_revenue_report_pdf(revenue_report_data, booking_status):
    
    admin_id = current_user.id

    # create PDF footer
    pdf = PDFWithFooter(admin_id)

    # create a new page
    pdf.add_page()

    # add a logo
    pdf.image("APP\static\Plan-ItRight.jpg", x=10, y=10, w=50, h=50)

    # title
    pdf.set_font("Arial", size=20)
    pdf.cell(200, 60, txt="Revenue Report", ln=True, align='C')

    # Add header row
    pdf.set_font("Arial", size=13)
    pdf.ln(10)  # optional: add a line break for spacing
    pdf.set_fill_color(227, 218, 225)  # set a fill color for the header row, optional
    pdf.cell(50, 10, txt="Venue ID", fill=True)
    pdf.cell(100, 10, txt="Venue Name", fill=True)
    pdf.cell(50, 10, txt="Total Revenue", fill=True)
    pdf.ln(10)  # move to the next line after headers
    
    # Add each data row to the PDF.
    pdf.set_font("Arial", size=13)
    for row in revenue_report_data:
        pdf.ln(10)
        pdf.cell(50, 10, txt=str(row[0]))
        pdf.cell(100, 10, txt=row[1])
        pdf.cell(50, 10, txt=str(row[2]))
    
    response = make_response(pdf.output(dest='S').encode('latin1'))
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"inline; filename={booking_status}_revenue.pdf"
    return response

def generate_popularity_report_pdf(popularity_report_data):
    
    admin_id = current_user.id

    # create PDF footer
    pdf = PDFWithFooter(admin_id)

    # create a new page
    pdf.add_page()

    # add a logo
    pdf.image("APP\static\Plan-ItRight.jpg", x=10, y=10, w=50, h=50)

    # title
    pdf.set_font("Arial", size=20)
    pdf.cell(200, 60, txt="Popularity Report", ln=True, align='C')

    # Add header row
    pdf.set_font("Arial", size=13)
    pdf.ln(10)  # optional: add a line break for spacing
    pdf.set_fill_color(227, 218, 225)  # set a fill color for the header row, optional
    pdf.cell(50, 10, txt="Venue ID", fill=True)
    pdf.cell(100, 10, txt="Venue Name", fill=True)
    pdf.cell(80, 10, txt="Total Booking", fill=True)
    pdf.cell(80, 10, txt="Percentage", fill=True)
    pdf.cell(80, 10, txt="Total Revenue", fill=True) #Not working at present needs follow up
    pdf.ln(10)
    
    # Add each data row to the PDF.
    pdf.set_font("Arial", size=13)
    for row in popularity_report_data:
        pdf.ln(10)
        pdf.cell(50, 10, txt=str(row[0]))
        pdf.cell(100, 10, txt=row[1])
        pdf.cell(80, 10, txt=str(row[2]))
        pdf.cell(80, 10, txt=str(row[3]))
        pdf.cell(80, 10, txt=str(row[4]))
    
    response = make_response(pdf.output(dest='S').encode('latin1'))
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"inline; filename=popularity_report.pdf"
    return response

@admin_bp.route('/report', methods=['GET', 'POST'])
@login_required
def generate_report():
    unread_messages_count = get_unread_messages_count(current_user.id)
    msg = ""
    date_format = "%Y-%m-%d"
    anAdmin = admin.get_admin_info(current_user.id)

    if request.method == 'POST':
        
        report_type = request.form['report_type']
        booking_status = request.form['booking_status']
        starting_date = request.form['starting_date']
        end_date = request.form['end_date']
        
        try:
            start_date_obj = datetime.strptime(starting_date, date_format)
            end_date_obj = datetime.strptime(end_date, date_format)
        except ValueError:
            msg = "Invalid date format. Please use YYYY-MM-DD."
            return render_template('admin/report.html', msg=msg, anAdmin = anAdmin)
        
        if start_date_obj > end_date_obj:
            msg = "End date must be later than the starting date. Please retry!"
            return render_template('admin/report.html', msg=msg, anAdmin = anAdmin)
        
        if report_type == "revenue":
            revenue_report = admin.view_revenue_report(booking_status, start_date_obj, end_date_obj)
            if revenue_report is not None:
                allVenues_labels =  [entry[1] for entry in revenue_report]
                allRevenue_data = [entry[2] for entry in revenue_report] 

                allVenues_labels_json = json.dumps(allVenues_labels)
                allRevenue_data_json = json.dumps(allRevenue_data, default = decimal_default)

                starting_date = datetime.strptime(starting_date, '%Y-%m-%d').strftime('%d-%m-%Y')
                end_date = datetime.strptime(end_date, '%Y-%m-%d').strftime('%d-%m-%Y')
                if 'export_pdf' in request.form:
                    pdf_yes = request.form['export_pdf']
                    if pdf_yes:
                        return generate_revenue_report_pdf(revenue_report, booking_status)
                return render_template('admin/get_report.html', anAdmin = anAdmin, msg = msg, 
                                    starting_date =  starting_date, end_date = end_date, 
                                    booking_status = booking_status,
                                    revenue_report = revenue_report, 
                                    allVenues_labels_json = allVenues_labels_json,
                                    allRevenue_data_json = allRevenue_data_json, unread_messages_count = unread_messages_count)
            else:
                msg = "There is no data in the selected date and type." 
            return render_template('admin/get_report.html', msg = msg, anAdmin = anAdmin, unread_messages_count = unread_messages_count)
         
        elif report_type == "popularity":
            popularity_report = admin.view_popularity_report(start_date_obj, end_date_obj)
            
            if popularity_report is not None:
                popularity_report_data = []
                popularity_report_labels = []
                for entry in popularity_report:
                    # Convert datetime objects to strings if necessary
                    popularity_report_data.append({
                        "Venue Name": entry[1],
                        "Number of Bookings": entry[2],
                        "Percentage of Total": f"{entry[3]:.2f}%",
                        "Average Revenue": entry[4]})
                    popularity_report_labels_json = json.dumps(popularity_report_labels)
                    popularity_report_data_json = json.dumps(popularity_report_data, default=decimal_default)
                if 'export_pdf' in request.form:
                    pdf_yes = request.form['export_pdf']
                    if pdf_yes:
                        return generate_popularity_report_pdf(popularity_report)
                return render_template('admin/get_report.html', msg = msg, anAdmin = anAdmin, popularity_report_labels_json = popularity_report_labels_json, popularity_report_data_json = popularity_report_data_json, popularity_report = popularity_report, unread_messages_count = unread_messages_count)
            else:
                msg = "There is no data in the selected date and type." 
            return render_template('admin/report.html', msg = msg, anAdmin = anAdmin)
    return render_template('admin/report.html', msg = msg, anAdmin = anAdmin, unread_messages_count = unread_messages_count)
            
        
        
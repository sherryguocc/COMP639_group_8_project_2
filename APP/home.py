
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user
from .classes.admin_class import admin
from .classes.planner_class import Planner
from .classes.customer_class import Customer
from .classes.venue_model import Venue
from.classes.booking_service_class import BookingService
from .classes.notification_model import Notifications
from datetime import date
import re


bp = Blueprint('home', __name__)

def get_unread_messages_count(customerID):
    try:
        # Get the ID of the currently logged-in customer
        customerID = current_user.id
        
        # Create an instance of the Notifications class
        unread = Notifications()
        
        # Get the count of unread messages for the customer
        unread_count = unread.unread_message_count_customer(customerID)

        return unread_count
    except Exception as e:
        # Handle exceptions and display an error flash message
        flash(str(e), "An error occurred while processing your request.")
        print(f"Exception occurred: {str(e)}")

# Display the venue list on the home page
@bp.route('/')
def home():
    
    anAdmin = None
    aPlan = None
    aCust = None
    unread_messages_count = None

    if current_user.is_authenticated:
        # Fetch user details based on their role, e.g., from a database
        if current_user.role == "admin":
            anAdmin = admin.get_admin_info(current_user.id)
            unread_messages_count = get_unread_messages_count(current_user.id)
        elif current_user.role == "planner":
            aPlan =  Planner.get_plan_info(current_user.id)
            unread_messages_count = get_unread_messages_count(current_user.id)
        elif current_user.role == "customer":
            aCust =  Customer.get_cust_info(current_user.id)
            unread_messages_count = get_unread_messages_count(current_user.id)

    # Get filter index
    sort_column = request.args.get('sort_column', 'default_column')
    sort_direction = request.args.get('sort_direction', 'asc')
    
    # Get the list of venues from the Venue model
    venueList = Venue.get_venue_list()

    # Filter the venueList to include only active venues
    venueList = [venue for venue in venueList if venue.is_active]

    # Sort the list by filter index
    venueList = Venue.sort_venue_list(venueList, sort_column, sort_direction)

    # Only show active venues
    selected_status = 'active'  
    venueList = Venue.sort_venueList_by_status(venueList, selected_status)

    # Sort the list by type
    selected_type = request.args.get('type', 'all')
    venueList = Venue.sort_venueList_by_type(venueList, selected_type)

    # Paginate the venue list
    page = request.args.get('page', 1, type=int)
    per_page = 6

    # Paginate the venue list
    start_index = (page - 1) * per_page
    end_index = start_index + per_page

    paginated_venues = venueList[start_index:end_index]

    return render_template('base.html', 
                           venueList=paginated_venues, 
                           page=page, per_page=per_page, 
                           sort_column=sort_column, 
                           sort_direction=sort_direction, 
                           selected_type=selected_type, 
                           selected_status=selected_status, 
                           anAdmin = anAdmin,
                           aPlan = aPlan,
                           aCust = aCust,
                           unread_messages_count=unread_messages_count)

#search function on the public home page
@bp.route('/', methods=['GET', 'POST'])
def search_venues_route():
    try:
        anAdmin = None
        aPlan = None
        aCust = None
        venues = None
        unread_messages_count = None

        if current_user.is_authenticated:
        # Fetch user details based on their role, e.g., from a database
            if current_user.role == "admin":
                anAdmin = admin.get_admin_info(current_user.id)
                unread_messages_count = get_unread_messages_count(current_user.id)
            elif current_user.role == "planner":
                aPlan =  Planner.get_plan_info(current_user.id)
                unread_messages_count = get_unread_messages_count(current_user.id)
            elif current_user.role == "customer":
                aCust =  Customer.get_cust_info(current_user.id)
                unread_messages_count = get_unread_messages_count(current_user.id)


        if request.method == 'POST':
            search_query = request.form.get('search_query')
            print(f"Search Query: {search_query}")
            
            venues = Venue.search(search_query)
            print(f"Venues: {venues}") 
            
            if not venues:
                flash('No matching venues found, sorry!')
                return redirect(url_for('home.home'))
    
    except Exception as e:
        flash(str(e), "An error occured while processing your request.")
        return redirect (url_for('home.home'))
    
    return render_template('base.html', venues=venues,
                                        anAdmin = anAdmin,
                                        aPlan = aPlan,
                                        aCust = aCust, 
                                        unread_messages_count = unread_messages_count)

#Display limited information for the public
@bp.route('/view/venues/<int:venueID>', methods=['GET', 'POST'])
def view_venues(venueID):
    try:
        venue = Venue.get_venue_by_id(venueID)
        anAdmin = None
        aPlan = None
        aCust = None
        venues = None

        unread_messages_count = None

        if current_user.is_authenticated:
            # Fetch user details based on their role, e.g., from a database
            if current_user.role == "admin":
                anAdmin = admin.get_admin_info(current_user.id)
                unread_messages_count = get_unread_messages_count(current_user.id)
            elif current_user.role == "planner":
                aPlan =  Planner.get_plan_info(current_user.id)
                unread_messages_count = get_unread_messages_count(current_user.id)
            elif current_user.role == "customer":
                aCust =  Customer.get_cust_info(current_user.id)
                unread_messages_count = get_unread_messages_count(current_user.id)


    except Exception as e:
        flash(str(e), "An error occured while processing your request.")
        return redirect (url_for('home.home'))
    
    return render_template('venue_detail.html', venue = venue, 
                                                venueID = venueID,
                                                anAdmin = anAdmin,
                                                aPlan = aPlan,
                                                aCust = aCust, 
                                                unread_messages_count = unread_messages_count)


@bp.route('/send_enquiry', methods=['GET', 'POST'])
def send_enquiry():
    msg = ''

    if request.method == 'POST':
        guest_title = request.form.get('guest_title')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        enquiry = request.form.get('enquiry')
        phone = request.form.get('phone')
        agree_email = request.form.get('agree_email')

        error_messages = []

        # Check for required fields
        required_fields = [guest_title, first_name, last_name, email, enquiry]
        if not all(required_fields):
            error_messages.append('Please enter all the required fields.')

        if not agree_email:
            error_messages.append('Please agree to the terms and conditions.')

        # Validate Phone number
        if phone:
            if not re.match(r'^\d+$', phone):
                error_messages.append('Invalid phone format.')
            elif len(phone) > 15:
                error_messages.append('The phone number is too long. Please check and re-enter.')
        else:
            phone = None
            phone_text = 'N/A'

        # Validate name
        if not re.match(r'^[A-Za-z]+$', first_name) or not re.match(r'^[A-Za-z]+$', last_name):
            error_messages.append('Names should only consist of letters.')

        # Validate email
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            error_messages.append('Invalid email format.')

        if error_messages:
            for message in error_messages:
                flash(message)
            return render_template('send_enquiry.html', msg=msg)

        # update information
        FirstName = first_name.title()
        LastName = last_name.title()

        today = date.today()
        formatted_date = today.strftime("%d-%m-%Y")
        enquiry = formatted_date + " - " + enquiry + " -- From Guest: " + FirstName + ' ' + LastName + "  Email: " + email + "  Phone: " + phone_text
        guestID = BookingService.create_guest(guest_title, FirstName, LastName, email, enquiry, phone)
        adminID = 1
        BookingService.guest_insert_reminder(today, guestID, adminID, enquiry)
        msg = 'Thank you for your enquiry. Your message has been sent successfully. Our team will get in touch with you at the earliest convenience.'

    return render_template('send_enquiry.html', msg=msg)


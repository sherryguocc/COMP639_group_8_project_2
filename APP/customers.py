
from flask import Blueprint, render_template, redirect, url_for, flash, request, make_response
from flask_login import current_user, login_required
from datetime import datetime, date, timedelta
from fpdf import FPDF
import re
import bcrypt
from decimal import Decimal
from .classes.venue_model import Venue
from.classes.additional_service_model import Decoration, Menu
from.classes.booking_service_class import BookingService
from.classes.notification_model import Notifications
from .classes.customer_class import Customer
from .classes.quote_model import Quote
from .classes.payment_model import Payment
from .classes.calendar_model import Calendar


cust_bp =  Blueprint('customer', __name__)



# Route for the customer dashboard page
@cust_bp.route('/home', methods=['GET'])
@login_required
def home():
    try: 
        aCust = Customer.get_cust_info(current_user.id)
        unread_messages_count = get_unread_messages_count(current_user.id)
        
        if aCust is None:
            flash ('No user data found!')
            return redirect (url_for('home.home'))
    except Exception as e:
        flash (str(e), "An error occured while processing your request.")
        return redirect (url_for('home.home'))
    return render_template('customer/home.html', aCust = aCust, unread_messages_count=unread_messages_count)

@cust_bp.route('/home', methods=['GET', 'POST'])
def search_venues_route():
    try:
        aCust = Customer.get_cust_info(current_user.id)
        unread_messages_count = get_unread_messages_count(current_user.id)
        venues = None
        if request.method == 'POST':
            search_query = request.form.get('search_query')
            print(f"Search Query: {search_query}")
            
            venues = Venue.search(search_query)
            print(f"Venues: {venues}") 
            
            if not venues:
                flash('No matching venues found, sorry!')
                return redirect(url_for('customer.home', aCust = aCust, unread_messages_count=unread_messages_count))
    
    except Exception as e:
        flash(str(e), "An error occured while processing your request.")
        return redirect (url_for('customer.home', aCust = aCust, unread_messages_count=unread_messages_count))
    
    return render_template('customer/home.html',  unread_messages_count=unread_messages_count, aCust = aCust, venues=venues)


@cust_bp.route('/edit_profile/<int:customerID>', methods=['GET', 'POST'])
@login_required
def edit_profile(customerID):
    msg = ''
    
    aCust = Customer.get_cust_info(customerID)
    unread_messages_count = get_unread_messages_count(customerID)
    
    if request.method == 'POST':
        Title = request.form.get('title')
        FirstName = request.form.get('first_name')
        LastName = request.form.get('last_name')
        Email = request.form.get('email')
        Phone = request.form.get('phone')
        Address = request.form.get('address')
        DOB = request.form.get('dob')

        # Necessary fields validation
        if not all([Title, FirstName, LastName, Email]):
            msg = "Please make sure all the required fields are filled out."
        
        # Firstname and lastname validation
        elif not re.match(r'^[A-Za-z]+$', FirstName) or not re.match(r'^[A-Za-z]+$', LastName):
            msg = "Name should only consist of letters."

        # Email validation
        elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', Email):
            msg = "Invalid email format."

        # Phone validation
        elif Phone and not re.match(r'^\d+$', Phone):
            msg = "Invalid phone format."
        elif Phone and len(str(Phone)) > 15:
            msg = "The phone number is too long. Please check and re-enter."

        # DOB validation
        elif DOB:
            dob_date = datetime.strptime(DOB, '%Y-%m-%d').date()
            today = date.today()
            if dob_date > today:
                msg = "Date of Birth must be today or earlier."

        # If all validations pass, perform the update operation
        if not msg:
            FirstName = FirstName.title()
            LastName = LastName.title()

            if not DOB:
                sql_dob = None
            else:
                dob_obj = datetime.strptime(DOB, '%Y-%m-%d')
                sql_dob = dob_obj.strftime('%Y-%m-%d')  # Convert date into SQL format

            try:
                Customer.customer_edit_profile(customerID, Title, FirstName, LastName, Phone, Email, Address, sql_dob)
                msg = 'Great! Your profile has been updated.'
                return redirect(url_for('customer.home', aCust=aCust, unread_messages_count=unread_messages_count, customerID=current_user.id))
            except Exception as e:
                msg = str(e)
                flash(msg, "An error occurred while processing your request.")
        
    return render_template('customer/edit_profile.html', customerID=current_user.id, aCust=aCust, msg=msg, unread_messages_count=unread_messages_count)



def is_valid_password(password):
    # check password length
    if len(password) < 8:
        return False
    # check password format
    if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)', password):
        return False
    return True

# Route to allow customer to change password
@cust_bp.route('/change_password/<int:customerID>', methods=['GET', 'POST'])
@login_required
def change_password(customerID):
    msg = ''
    aCust = Customer.get_cust_info(customerID)
    unread_messages_count = get_unread_messages_count(customerID)
    if request.method == 'POST':
        if not all(request.form.get(field) for field in ['old_password', 'new_password', 'confirm_new_password']):
            msg = 'Please fill out all the fields.'
        else:
            # Retrieve user input from the form.
            old_password = request.form.get('old_password')
            new_password = request.form.get('new_password')
            confirm_new_password = request.form.get('confirm_new_password')

            # Retrieve the user's current password hash from the database
            current_password_hash = aCust[10]

            # Check if the old password matches record in database
            if bcrypt.checkpw(old_password.encode('utf-8'), current_password_hash.encode('utf-8')):
        
                # check if password is in valid format
                if not is_valid_password(new_password):
                    msg = 'Password must be at least 8 digit with both letters and numbers.'
                    return render_template('customer/change_password.html', msg=msg, aCust = aCust, unread_messages_count=unread_messages_count)

                # Check if the new password and confirm new password match
                if confirm_new_password == new_password:

                    # Old password matches, proceed to update the password
                    # Hash the new password using bcrypt
                    hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                    # Update the user's password in the database
                    Customer.customer_change_password(hashed_new_password, customerID)

                    flash('Password updated successfully!')
                    return redirect(url_for('customer.home', customerID = current_user.id, aCust = aCust, unread_messages_count = unread_messages_count))
                
                else:
                    msg = 'Please confirm, the new passwords do not match'
                    # return render_template('customer/change_password.html', msg=msg, aCust = aCust)
            
            else:
                # Old password does not match, show an error message
                msg = 'Your old password is incorrect'
                # return render_template('customer/change_password.html', msg=msg, aCust = aCust)
                     
    return render_template ('customer/change_password.html',  msg=msg, aCust = aCust, unread_messages_count=unread_messages_count)


# List of available venues
@cust_bp.route('/venue_list')
@login_required
def venue_list():
    aCust= Customer.get_cust_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    # get fileter index
    sort_column = request.args.get('sort_column', 'default_column')
    sort_direction = request.args.get('sort_direction', 'asc')
    # Get the list of venues from the Venue model
    venueList = Venue.get_venue_list()

    # show active venues only
    selected_status = 'active' 
    venueList = Venue.sort_venueList_by_status(venueList, selected_status)

    # sorted the list by filter index
    venueList = Venue.sort_venue_list(venueList, sort_column, sort_direction)
    # sorted the list by type
    selected_type = request.args.get('type', 'all')
    venueList = Venue.sort_venueList_by_type(venueList, selected_type)
    
    #Paginate the venue list
    page = request.args.get('page', 1, type=int)
    per_page = 5

    #Paginate the venue list
    start_index = (page-1)* per_page
    end_index = start_index + per_page

    paginated_venues = venueList[start_index:end_index]
    return render_template('customer/venue_list.html', aCust=aCust, venueList=paginated_venues, page=page, per_page=per_page, sort_column=sort_column, sort_direction=sort_direction, selected_type=selected_type, selected_status=selected_status, unread_messages_count=unread_messages_count)

@cust_bp.route('/venue_detail/<int:venueID>', methods=['GET', 'POST'])
@login_required
def view_venues(venueID):
    aCust= Customer.get_cust_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    try:
        venue = Venue.get_venue_by_id(venueID)

    except Exception as e:
        flash(str(e), "An error occured while processing your request.")
        return redirect (url_for('customer.home'))
    
    return render_template('customer/venue_detail.html', venue = venue, venueID = venueID, aCust=aCust, unread_messages_count=unread_messages_count)

# Route for booking a venue
@cust_bp.route('/book/venue/<int:venueID>', methods=['GET', 'POST'])
def book_venue(venueID):
    unread_messages_count = get_unread_messages_count(current_user.id)
    if current_user.is_authenticated:
        aCust = Customer.get_cust_info(current_user.id)
        calendar_dict= Calendar.fetch_calendar_data(venueID)
        try:
            # Update venue status based on today's date
            BookingService.update_venue_rented_status_based_on_end_date()

            # Fetch information about the selected venue by venueID
            selected_venue = Venue.get_venue_by_id(venueID)

            # Fetch the booking end date for date comparison validation later
            booking_end_date = BookingService.get_booking_end_date_by_venue_id(venueID)

            # Fetch all decorations and food menus
            decoration = Decoration.get_all_decorations()
            food_menu = Menu.get_all_menus()
            
            # Fetch default menu
            default_menu_id = 1
            default_menu = Menu.get_image_by_food_id(default_menu_id)

            if request.method == 'POST':
                # Handle the POST request for booking
                customer = current_user.id
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
                    return redirect(url_for('customer.book_venue', venueID= venueID, aCust = aCust, selected_venue=selected_venue, decoration=decoration, food_menu=food_menu))


                guest_number = request.form.get('guestsNumber')
                event_details = request.form.get('comments')
                status = "Pending"

                # Validation
                if not all([event_date, event_time, end_date, end_time, guest_number]):
                    flash("The required fields must be filled in.", 'error')
                    return redirect(url_for('customer.book_venue', venueID= venueID, aCust = aCust, selected_venue=selected_venue, decoration=decoration, food_menu=food_menu))

                if event_date_object < datetime.now().date() or end_date_object < datetime.now().date():
                    flash("Please select a future date.")
                    return redirect(url_for('customer.book_venue', venueID= venueID, aCust = aCust, selected_venue=selected_venue, decoration=decoration, food_menu=food_menu))

                if event_date_object > end_date_object:
                    flash("Invalid! End date must be after start date!")
                    return redirect(url_for('customer.book_venue', venueID= venueID, aCust = aCust, selected_venue=selected_venue, decoration=decoration, food_menu=food_menu))

                if event_date_object == end_time_object:
                    if event_time_object > end_time_object:
                        flash("Invalid! End time must be after start time!")
                        return redirect(url_for('customer.book_venue', venueID= venueID, aCust = aCust, selected_venue=selected_venue, decoration=decoration, food_menu=food_menu))

                if selected_venue.get_rented == 1 and booking_end_date[0] > datetime.now().date():
                    flash("This venue is currently on hire. Please choose a different venue.")
                    return redirect(url_for('customer.book_venue', venueID= venueID, aCust = aCust, selected_venue=selected_venue, decoration=decoration, food_menu=food_menu))

                if int(guest_number) > selected_venue.get_maxCapacity:
                    flash('Sorry, guest number exceeds the maximum capacity of the venue. Please choose a different venue.')
                    return redirect(url_for('customer.book_venue', venueID= venueID, aCust = aCust, selected_venue=selected_venue, decoration=decoration, food_menu=food_menu))
                

                if not event_details:
                    event_details = None

                decoration = request.form.get('decoration')
                food = request.form.get('food')

                if not decoration:
                    decoration = None

                if not food:
                    food = None

                if not BookingService.is_venue_available(venueID, event_date_db, end_date_db):
                    flash("The venue is already booked for the chosen date")
                    return redirect(url_for('customer.book_venue', venueID= venueID, aCust = aCust, selected_venue=selected_venue, decoration=decoration, food_menu=food_menu))
                else:
                    if decoration is not None and food is not None:
                        # Insert booking with food and decoration
                        booking_id = BookingService.create_booking(customer, event_date_db, event_time_db, end_date_db, end_time_db, guest_number, event_details, status)
                        ref_num = BookingService.create_or_get_reference_number(booking_id)
                        venueorder_id = BookingService.create_venue_order(venue, booking_id)
                        decor_order_id = BookingService.create_decor_order(booking_id, decoration)
                        menu_order_id = BookingService.create_menu_order(booking_id, food)
                        BookingService.update_booking(booking_id, venueorder_id, menu_order_id, decor_order_id)
                        Calendar.insert_booked_calendar(booking_id)
                        flash("Booking Successful!")
                        return redirect(url_for('customer.booking_details', aCust = aCust, customerID=current_user.id))
                    
                    elif decoration is not None:
                        # Insert booking with only decoration
                        booking_id = BookingService.create_booking(customer, event_date_db, event_time_db, end_date_db, end_time_db, guest_number, event_details, status)
                        ref_num = BookingService.create_or_get_reference_number(booking_id)
                        venueorder_id = BookingService.create_venue_order(venue, booking_id)
                        decor_order_id = BookingService.create_decor_order(booking_id, decoration)
                        BookingService.update_booking(booking_id=booking_id, venueorder_id=venueorder_id, decor_order_id=decor_order_id)
                        Calendar.insert_booked_calendar(booking_id)
                        flash("Booking Successful!")
                        return redirect(url_for('customer.booking_details', aCust = aCust, customerID=current_user.id))

                    elif food is not None:
                        # Insert booking with only food menu
                        booking_id = BookingService.create_booking(customer, event_date_db, event_time_db, end_date_db, end_time_db, guest_number, event_details, status)
                        ref_num = BookingService.create_or_get_reference_number(booking_id)
                        venueorder_id = BookingService.create_venue_order(venue, booking_id)
                        menu_order_id = BookingService.create_menu_order(booking_id, food)
                        BookingService.update_booking(booking_id=booking_id, venueorder_id=venueorder_id, menu_order_id=menu_order_id)
                        Calendar.insert_booked_calendar(booking_id)
                        flash("Booking Successful!")
                        return redirect(url_for('customer.booking_details', aCust = aCust, customerID=current_user.id))
                    
                    else:
                        # Insert booking with no decoration and no food menu
                        booking_id = BookingService.create_booking(customer, event_date_db, event_time_db, end_date_db, end_time_db, guest_number, event_details, status)
                        ref_num = BookingService.create_or_get_reference_number(booking_id)
                        venueorder_id = BookingService.create_venue_order(venue, booking_id)
                        BookingService.update_booking(booking_id, venueorder_id)
                        Calendar.insert_booked_calendar(booking_id)
                        flash("Booking Successful!")
                        return redirect(url_for('customer.booking_details', aCust = aCust, customerID=current_user.id))

        except Exception as e:
            print(f"Exception occurred: {e}")
            flash(f"An error: {e}  occurred while processing your request.")
            return redirect(url_for('customer.home', aCust = aCust, customerID=current_user.id))

        menus_with_index = [{"index": index, "menu": menu} for index, menu in enumerate(food_menu)]
        return render_template('customer/book_venue.html',
                               aCust = aCust, calendar_dict=calendar_dict,
                               selected_venue=selected_venue, 
                               decoration=decoration, 
                               food_menu=food_menu, 
                               default_menu=default_menu,
                               menus=menus_with_index,
                               unread_messages_count=unread_messages_count)
    else:
        return redirect(url_for('auth.login'))
    
    

# Function to fetch bookings for a customer
def get_bookings_for_customer(customerID):
    today = datetime.today()
    current_time = datetime.now().time()
    bookings = BookingService.show_booking_details(customerID, today, current_time)
    booking_list = [{'details': details, 'ref_number': details[12]} for details in bookings]
    return booking_list

# Function to generate a PDF receipt for a customer
def generate_pdf_for_customer(customerID):
    bookings = get_bookings_for_customer(customerID)  # Fetch the bookings from the database

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.image("APP\static\Plan-ItRight.jpg", x=10, y=10, w=50, h=50)

    for booking in bookings:
        ref_number = booking['ref_number']
        details = booking['details']
        pdf.cell(200, 10, txt=f"Booking Reference Number: {ref_number}", ln=True, align='C')
        
        planner =  details[0] if details[0] else 'Yet to be assigned'
        venue = details[1] 
        location = details[2]
        venue_fee = details[18]
        menu = details [4] if details[4] else 'N/A'
        food_price = details[15]
        decoration = details [6] if details[6] else 'N/A'
        decoration_fee = details[14]
        start_date = details[7]
        start_time = details [8]
        end_date = details [9]
        end_time = details [10]
        guest_number = details [11]

        # Add booking details to the PDF
        pdf.cell(0, 10, txt=f"Planner: {planner}", ln=True)
        pdf.cell(0, 10, txt=f"Venue: {venue}", ln=True)
        pdf.cell(0, 10, txt=f"Location: {location}", ln=True)
        pdf.cell(0, 10, txt=f"Venu Hiring Fee: {venue_fee}", ln=True)
        pdf.cell(0, 10, txt=f"Menu: {menu}", ln=True)
        pdf.cell(0, 10, txt=f"Estimated food price for guests: {food_price}", ln=True)
        pdf.cell(0, 10, txt=f"Decoration/Styling: {decoration}", ln=True)
        pdf.cell(0, 10, txt=f"Decor/stying Fee: {decoration_fee}", ln=True)
        pdf.cell(0, 10, txt=f"Start Date: {start_date}", ln=True)
        pdf.cell(0, 10, txt=f"Start Time: {start_time}", ln=True)
        pdf.cell(0, 10, txt=f"End Date: {end_date}", ln=True)
        pdf.cell(0, 10, txt=f"End Time: {end_time}", ln=True)
        pdf.cell(0, 10, txt=f"Guest Number: {guest_number}", ln=True)
        # Add a line to separate bookings
        pdf.ln(10)
    # Prepare the PDF response
    response  = make_response(pdf.output(dest='S').encode('latin1'))
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"inline; filename=customer_{customerID}_bookings.pdf"
    return response

#Booking details route
@cust_bp.route('/booking/details/<int:customerID>', methods = ['GET', 'POST'])
@login_required
def booking_details(customerID):
    aCust = Customer.get_cust_info(customerID)
    unread_messages_count = get_unread_messages_count(current_user.id)
    booking = []
    historical_bookings  = []

    try:
        today = datetime.today()
        current_time = datetime.now().time()

        # Fetch upcoming bookings for the customer
        bookings = BookingService.show_booking_details(customerID, today, current_time)
        for details in bookings:
            ref_number = details[12]
            booking.append({'details': details, 'ref_number': ref_number})

        # Fetch historical bookings for the customer
        previous_bookings = BookingService.show_historical_bookings(customerID, today, current_time)
        for details in previous_bookings:
            ref_number = details[12]
            historical_bookings.append({'details': details, 'ref_number': ref_number})

        if request.method == 'POST':
            if 'export_method' in request.form:
                # Generate and return a PDF of booking details for the customer
                response = generate_pdf_for_customer(customerID)
                return response

    except Exception as e:
        flash(str(e), "An error occurred while processing your request.")
        print(f"Error: {e}")  
    return render_template('customer/booking_details.html', aCust = aCust, booking_details=booking, historical_bookings=historical_bookings, unread_messages_count=unread_messages_count)

#Customer view messages route
@cust_bp.route('/view/messages/<int:customerID>')
@login_required
def view_messages(customerID):
    aCust = Customer.get_cust_info(customerID)
    messages = []  # Default empty list
    try:
        
        notifications = Notifications()  
        all_messages = notifications.customer_view_messages(customerID)
        unread_messages_count = get_unread_messages_count(current_user.id)

        
        # Prepare a list of messages with relevant details
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
        return redirect(url_for('customer.home', aCust= aCust, error_message=str(e)))  

    return render_template('customer/messagebox.html', aCust = aCust, messages=messages, unread_messages_count=unread_messages_count)

@cust_bp.route('/mark_as_read/<int:reminderID>', methods=['POST'])
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

@cust_bp.route('/delete_message/<int:reminderID>', methods=['POST'])
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


#CUSTOMER UPDATE BOOKINGS ROUTE
@cust_bp.route('/update/bookings/<int:bookingID>', methods=['GET','POST'])
@login_required
def edit_bookings(bookingID):
    aCust = Customer.get_cust_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    print("Starting edit_bookings function...")

    # Fetch the current booking details
    current_booking = BookingService.get_booking_by_id(bookingID)
    print("Retrieved current booking:", current_booking)

    # Check if the booking exists
    if not current_booking:
        print("No booking found!")
        flash("No booking found", "error")
        return redirect(url_for('customer.booking_details', customerID=current_user.id))

    # Fetch associated information about the booking
    current_venue = current_booking[1]
    current_menu = current_booking[4]
    current_decor = current_booking[7]
    selected_venue = Venue.get_venue_by_id(current_venue)
    print("Selected venue:", selected_venue.get_venueID)

    # Return the default template first
    all_venue = Venue.get_venue_list()
    all_decoration = Decoration.get_all_decorations()
    all_food_menu = Menu.get_all_menus()

    #Converting time format as apparently HTML does not accept 0:00:00 but 00:00:00 (unsure why missing leading 0 for start time)
    #The zfill(len) method adds zeros (0) at the beginning of the string, until it reaches the specified length which is two in this case.
    start_time_value = str(current_booking[9])
    start_time_value_padded = ':'.join([i.zfill(2) for i in start_time_value.split(':')])

    end_time_value = str(current_booking[11])
    end_time_value_padded = ':'.join([i.zfill(2) for i in end_time_value.split(':')])

    if request.method == 'POST':
        print("Processing POST request...")
        
        # Extract event start and end date
        event_date = request.form.get('startDate')
        event_date_object = datetime.strptime(event_date, '%Y-%m-%d').date()
        print("Event Date:", event_date_object)

        end_date = request.form.get('endDate')
        end_date_object = datetime.strptime(end_date, '%Y-%m-%d').date()
        print("End Date:", end_date_object)

        # Extract event start and end time
        event_time = request.form.get('startTime')
        try:
            event_time_object = datetime.strptime(event_time, '%H:%M').time()
        except ValueError:
            event_time_object = datetime.strptime(event_time, '%H:%M:%S').time()
        print("Event Time:", event_time_object)

        end_time = request.form.get('endTime')
        try:
            end_time_object = datetime.strptime(end_time, '%H:%M').time()
        except ValueError:
            end_time_object = datetime.strptime(end_time, '%H:%M:%S').time()
            print("End Time:", end_time_object)
        
        # For Dates
        event_date_db = event_date_object.strftime('%Y-%m-%d')
        end_date_db = end_date_object.strftime('%Y-%m-%d')

        # For Times
        event_time_db = event_time_object.strftime('%H:%M:%S')
        end_time_db = end_time_object.strftime('%H:%M:%S')

        guest_number = request.form.get('guestsNumber')

        # Check for missing fields
        if not all ([event_date, event_time, end_date, end_time]):
            print("Missing required fields")
            flash("The required fields must be filled in.", 'error')
            return redirect (url_for ('customer.edit_bookings',  aCust=aCust, bookingID = bookingID))

        # Check if selected dates are in the future
        if event_date_object < datetime.now().date() or end_date_object < datetime.now().date():
            flash("Please select a future date.")
            return redirect (url_for ('customer.edit_bookings',  aCust=aCust, bookingID = bookingID))

        # Check if end date/time is after start date/time
        if event_date_object > end_date_object:
            flash("Invalid! End date must be after start date!")
            return redirect (url_for ('customer.edit_bookings',  aCust=aCust, bookingID = bookingID))
        
        # Check if the event start date and end date are the same and if the event start time
        # is greater than or equal to the event end time.
        if event_date_object == end_date_object and event_time_object >= end_time_object:
            flash("Invalid! End time must be after start time!")
            return redirect (url_for ('customer.edit_bookings', aCust=aCust, bookingID = bookingID))
        
        # Get the maximum capacity of the selected venue. Check if the number of guests exceeds the maximum capacity of the venue.
        venue_max_capacity = selected_venue.get_maxCapacity 
        if int(guest_number) > venue_max_capacity:
            flash('Sorry, guest number exceeds the maximum capacity of the venue. For health and safety, please choose a different venue.')
            return redirect (url_for ('customer.edit_bookings',  aCust=aCust, bookingID = bookingID))
        
        # Get event details from the form, or set it to None if not provided.
        event_details = request.form.get('comments')
        if not event_details:
            event_details = None

        # Get the selected venue, decoration, and food menu from the form.
        venue_selected = request.form.get('venue')
        decoration_selected = request.form.get('decoration')
        food_selected = request.form.get('food')

        # Set decoration and food menu to None if not selected.
        if not decoration_selected:
            decoration_selected = None
        if not food_selected:
            food_selected = None

        # If the user chose to delete the booking and the booking hasn't been processed (not yet assigned), then proceed to delete
        if request.form.get('action') == 'delete' and not current_booking[16]:  
            print("Attempting to delete booking...")
            BookingService.delete_decor_order(bookingID)
            BookingService.delete_menu_order(bookingID)
            BookingService.delete_booking(bookingID)
            BookingService.delete_venue_order(bookingID)
            Calendar.delete_calendar_due_to_booking(bookingID)
            flash('Booking deleted successfully!', 'success')
            return redirect(url_for('customer.booking_details', customerID=current_user.id))

        successful_update = True

        # Update the core booking details
        BookingService.update_booking_details(bookingID, event_date_db, event_time_db, end_date_db, end_time_db, guest_number, event_details)
        Calendar.delete_calendar_due_to_booking(bookingID)
        Calendar.insert_booked_calendar(bookingID)

        # Check if the venue has changed and if so, update
        if venue_selected != current_venue:
            BookingService.update_venue_order(venue_selected, bookingID)
            #Calendar.update_canlendar_if_venue_change(venue_selected, bookingID)


        # For Decorations
        if current_decor is None and decoration_selected is not None:
            decor_order_id = BookingService.create_decor_order(bookingID, decoration_selected)
            BookingService.update_booking(bookingID, decor_order_id = decor_order_id)
        elif decoration_selected != current_decor:
            BookingService.update_decor_order(decoration_selected, bookingID)
        elif not decoration_selected:
            BookingService.delete_decor_order(bookingID)

        # For Food
        if current_menu is None and food_selected is not None:
            food_order_id = BookingService.create_menu_order(bookingID, food_selected)
            BookingService.update_booking(bookingID, menu_order_id=food_order_id)
        elif food_selected != current_menu:
            BookingService.update_menu_order(food_selected, bookingID)
        elif not food_selected:
            BookingService.delete_menu_order(bookingID)

        if successful_update: 
            flash('Booking updated succesfully!', 'success')
            return redirect (url_for('customer.booking_details', aCust=aCust, customerID=current_user.id))
        else:
            flash ('An error occurred while updating the booking.', 'error')
            return redirect (url_for('customer.edit_bookings', aCust = aCust, bookingID=bookingID, current_booking=current_booking, all_venue=all_venue, all_decoration=all_decoration, all_food_menu=all_food_menu, menus=menus_with_index, start_time = start_time_value_padded, end_time = end_time_value_padded))

    menus_with_index = [{"index": index, "menu": menu} for index, menu in enumerate(all_food_menu)]
    return render_template('customer/update_bookings.html',  aCust = aCust, bookingID=bookingID, current_booking=current_booking, all_venue=all_venue, all_decoration=all_decoration, all_food_menu=all_food_menu, menus=menus_with_index, start_time = start_time_value_padded, end_time = end_time_value_padded, unread_messages_count=unread_messages_count)


@cust_bp.route('view_my_quotes')
@login_required
def view_quote():
    unread_messages_count = get_unread_messages_count(current_user.id)
    try:
        aCust = Customer.get_cust_info(current_user.id)
        quotes = Quote.get_quote_by_customerID(current_user.id)
        print(quotes)

        today = date.today()
        quotes_with_status = [{
            'quote':quote,
            'expired': quote[8] < today
        } for quote in quotes]
    except Exception as e:
        # Handle exceptions and display an error flash message
        flash(str(e), "An error occurred while processing your request.")
        print(f"Exception occurred: {str(e)}")
    
    return render_template('customer/view_myquote.html', aCust = aCust, quotes_with_status=quotes_with_status, unread_messages_count=unread_messages_count)


@cust_bp.route('/view/myquote/<int:bookingID>', methods=['GET', 'POST'])
@login_required
def customer_view_quote(bookingID):
    unread_messages_count = get_unread_messages_count(current_user.id)
    try:
        aCust =  Customer.get_cust_info(current_user.id)
        aQuote = Quote.get_quote(bookingID)
        aBooking = BookingService.planner_check_booking_details(bookingID)
        print(aBooking)
        print(aQuote)
        amount = aQuote[12]
        print(type(amount))
        if request.method == 'POST':
            print("Received POST request")
            if 'export_method' in request.form:
                print("Found export_method in form")
                response = generate_quote_pdf(aQuote, aBooking)
                return response

            elif 'cancel_booking' in request.form:
                print("Processing cancel_booking request")
                
                # Logic for calculating refund
                current_date = date.today()
                NZ_formatted_date = current_date.strftime("%d-%m-%Y")
                print(f"Current date: {current_date}")

                event_date = aBooking[9]  # Assuming aBooking has event_date attribute
                print(f"Event date: {event_date}")
                print(f"Type of current_date: {type(current_date)}")
                print(f"Type of event_date: {type(event_date)}")


                days_difference = timedelta(days=(event_date - current_date).days)
                print(f"Type of days_difference: {type(days_difference)}")
                print(f"Days difference: {days_difference.days}")

                if days_difference.days  >= 14:  
                    refund_amount = aQuote[12] 
                elif days_difference.days  >= 7:
                    refund_amount = Decimal('0.50') * aQuote[12]
                else:
                    refund_amount =  Decimal('0.0')  # No refund if less than 7 days
                print(f"Calculated refund amount before making negative: {refund_amount}")

                update_amount = amount - refund_amount
                print(type(update_amount))
                print(f"Original amount: {amount} Refund amount: {refund_amount} Updated amount {update_amount}")

                # Merchant_Account = '0011111122334444'
                Payment.refund_booking(bookingID, update_amount, current_date)
                print("Payment refund booking completed")

                BookingService.update_status_for_refund(bookingID)
                print("Updated booking status for refund")

                print(f"Refunding {refund_amount} to customer.")
                insert_cancel_message = Notifications()
                message = f"{NZ_formatted_date} - Your booking for {aBooking[5]} has been cancelled, ${refund_amount} have been refunded to your account. Please feel free to contact us if you have any questions"
                insert_cancel_message.cancel_message(current_date, current_user.id, aBooking[18], message)
                return redirect (url_for('customer.view_quote'))

    except Exception as e:
        print(f"Exception encountered: {e}")
        flash(str(e), "An error occurred while processing your request.")
    
    return render_template('customer/view_quote.html', amount=aQuote[12], aQuote=aQuote, aBooking=aBooking, aCust=aCust, bookingID=bookingID, unread_messages_count=unread_messages_count)

def generate_quote_pdf (quote_details, booking_details):
    pdf = FPDF()
 
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin = 15)
    # add a logo
    pdf.image("APP\static\Plan-ItRight.jpg", x=10, y=10, w=50, h=50)

    # title of the PDF
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 60, txt="Quotation", ln=True, align='C')

    # Quoted for section
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(190, 10, "Quoted for", 0, 1)
    pdf.set_font("Arial", '', 12)
    pdf.cell(190, 10, booking_details[2], 0, 1)
    pdf.cell(190, 10, booking_details[16] if booking_details[16] else 'N/A', 0, 1)
    pdf.cell(190, 10, booking_details[3] if booking_details[3] else 'N/A', 0, 1)
    # Event Information section
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(190, 10, "Event Information", 0, 1)
    pdf.set_font("Arial", '', 12)
    pdf.cell(190, 10, f"Event Venue: {booking_details[5]}", 0, 1)
    pdf.cell(190, 10, f"Place of Event: {booking_details[6]}", 0, 1)
    pdf.cell(190, 10, f"Date of Event: {booking_details[9]}", 0, 1)
    pdf.cell(190, 10, f"Start Time: {booking_details[10]}", 0, 1)
    pdf.cell(190, 10, f"End Date: {booking_details[11]}", 0, 1)
    pdf.cell(190, 10, f"Finish Time: {booking_details[12]}", 0, 1)

    # Event Planning Pricing section
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(190, 10, "Event Planning Pricing", 0, 1)
    pdf.set_font("Arial", '', 12)
    pdf.cell(95, 10, "Venue Fee", 1)
    pdf.cell(95, 10, f"${quote_details[2]}", 1, 1)
    pdf.cell(95, 10, "Decoration Fee", 1)
    pdf.cell(95, 10, f"${quote_details[3]}", 1, 1)
    pdf.cell(95, 10, "Menu Price", 1)
    pdf.cell(95, 10, f"${quote_details[4]}", 1, 1)
    pdf.cell(95, 10, "Additional Requirements", 1)
    pdf.cell(95, 10, f"${quote_details[14]}", 1, 1)
    pdf.cell(95, 10, "Discounts", 1)
    pdf.cell(95, 10, f"${quote_details[6]}", 1, 1)
    pdf.cell(95, 10, "Total Before Tax", 1)
    pdf.cell(95, 10, f"${quote_details[10]}", 1, 1)
    pdf.cell(95, 10, "GST", 1)
    pdf.cell(95, 10, f"${quote_details[11]}", 1, 1)
    pdf.cell(95, 10, "Total After Tax", 1)
    pdf.cell(95, 10, f"${quote_details[12]}", 1, 1)

    # Terms and Conditions section
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(190, 10, "Terms and Conditions", 0, 1)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(190, 10, f" {quote_details[9]}", 0)
    pdf.cell(190, 10, f"Expiry Date for this Quotation: {quote_details[8]}", 0, 1)
    pdf.multi_cell(190, 10, "Event Changes: Any changes to the event details (like date, location, number of attendees) must be communicated in writing at least 14 days before the event.", 0)

    response = make_response(pdf.output(dest='S').encode('latin1'))
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"attachment; filename=Booking_No{booking_details[0]}.pdf"

    return response


@cust_bp.route('/payment/<int:bookingID>', methods=['GET', 'POST'])
def payment(bookingID):
    unread_messages_count = get_unread_messages_count(current_user.id)
    try:
        print("Entering the payment function...") # Debugging statement
        
        aCust =  Customer.get_cust_info(current_user.id)
        aQuote = Quote.get_quote(bookingID)
        aBooking = BookingService.planner_check_booking_details(bookingID)
        planner_id = aBooking[18]

        amount = aQuote[12]
        
        if request.method == 'POST':
            print("Processing POST request...") # Debugging statement
            
            part1 = request.form.get('part1')
            part2 = request.form.get('part2')
            part3 = request.form.get('part3')
            part4 = request.form.get('part4')
            bank_account = part1 + part2 + part3 + part4

            print(f"Bank Account: {bank_account}") # Debugging statement
            print(f"Amount: {amount}") # Debugging statement
            today = date.today()
            NZ_formatted_date = today.strftime("%d-%m-%Y")
            message_to_planner = f'{NZ_formatted_date} - Hi {aBooking[17]}, The payment for booking at {aBooking[5]} has been paid. -- From Customer {aBooking[1]} {aBooking[2]}'
            print(f"Today's date: {today}") # Debugging statement

            payment = Payment.pay_booking(bookingID, current_user.id, amount, bank_account, today)
            BookingService.update_status_after_payment(bookingID)

            # Send notification to planner 
            BookingService.customer_insert_reminder_to_planner(today, planner_id, message_to_planner)

            print("Payment processed successfully!") # Debugging statement

            flash("Payment Successful!", 'Success')
            return redirect(url_for('customer.home', aCust=aCust))

    except Exception as e:
        print(f"Error: {e}") # Debugging statement
        flash(str(e), "An error occured while processing your request.")

    return render_template('customer/view_quote.html', aQuote=aQuote, aBooking=aBooking, aCust=aCust, bookingID=bookingID, amount = amount, unread_messages_count=unread_messages_count)


@cust_bp.route('/send_enquiry', methods=['GET', 'POST'])
@login_required
def send_enquiry():
    msg=''
    aCust =  Customer.get_cust_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    if request.method == 'POST':
        enquiry = request.form.get('enquiry')
        today = date.today()
        formatted_date = today.strftime("%d-%m-%Y")
        if enquiry:
            enquiry = (formatted_date + " - "+ enquiry + "\n -- From Customer: " + str(aCust[0]) + ' ' + aCust[3] + ' ' + aCust[4])
            adminID = 1
            BookingService.customer_insert_reminder_to_admin(today, adminID, enquiry)
            msg = 'Thank you for your enquiry. Your message has been sent successfully. Our team will get in touch with you at the earliest convenience.'
        else:
            flash('Please fill out the enquiry message.')

    return render_template('customer/send_enquiry.html', aCust = aCust, msg=msg, unread_messages_count=unread_messages_count)

 
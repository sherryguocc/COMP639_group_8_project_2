import decimal
import json
from flask import Blueprint, render_template, redirect, url_for, flash, request, make_response
from flask_login import current_user, login_required
from datetime import datetime, timedelta
from fpdf import FPDF
import bcrypt
from.classes.booking_service_class import BookingService
from.classes.notification_model import Notifications
from.classes.planner_class import Planner
from.classes.venue_model import Venue
from.classes.customer_class import Customer
from.classes.quote_model import Quote
from .classes.additional_service_model import Menu, Decoration
from .classes.venue_model import Venue
import re
import os
import app
from werkzeug.utils import secure_filename


pl_bp = Blueprint('planner', __name__)


# Route for the planner home page
@pl_bp.route('/home', methods=['GET'])
@login_required
def home():
    try: 
        # get the planner object
        aPlan =  Planner.get_plan_info(current_user.id)
        unread_messages_count = get_unread_messages_count(current_user.id)
        # check if the planner exists in db
        if aPlan is None:
            flash ('No user data found!')
            return redirect (url_for('home.home', aPlan = aPlan))
    except Exception as e:
        flash (str(e), "An error occured while processing your request.")
        return redirect (url_for('home.home', aPlan = aPlan))
    return render_template('planner/home.html', aPlan = aPlan, unread_messages_count=unread_messages_count)
  

@pl_bp.route('/edit_profile/<int:plannerID>', methods=['GET', 'POST'])
@login_required
def edit_profile(plannerID):
    msg =''
    try: 
        aPlan = Planner.get_plan_info(current_user.id)
        unread_messages_count = get_unread_messages_count(current_user.id)
        # Get updated info from form
        if request.method == 'POST':
            Title = request.form.get('title')
            FirstName = request.form.get('first_name')
            LastName = request.form.get('last_name')
            Email = request.form.get('email')
            Phone = request.form.get('phone') 
            Address = request.form.get('address') 
            Description = request.form.get('description') 
            Photo = request.form.get('photo')

            # check if all the required fields are filled
            if not all([Title, FirstName, LastName, Email]):
                msg = "Please make sure all the required fields are filled out."

            # Phone, address, description and photo are not required fields
            if not Phone:
                Phone = None
            if not Address:
                Address = None
            if not Description:
                Description = None
            if not Photo:
                Photo = None

            else:
                # Validate firstname and lastname format
                if not re.match(r'^[A-Za-z]+$', FirstName) or not re.match(r'^[A-Za-z]+$', LastName):
                    msg = "Name should only consist of letters."
                
                # Validate Email Format
                elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', Email):
                    msg = "Invalid email format"

                # Validate Phone number
                elif Phone and not re.match(r'^\d+$', Phone):
                    msg = "Invalid phone format"
                # validate the length of phone number 
                elif Phone and len(str(Phone))>15:
                    msg = "The phone number is too long. Please check and re-enter."

               
            if not msg:
                FirstName = FirstName.title()
                LastName = LastName.title()
                # Update the planner's new info into database
                Planner.update_planner(Title, FirstName, LastName, Phone, Email, Address, Description, Photo, plannerID)

                msg = 'Great! Your profile has been updated.'
                return redirect(url_for('planner.home', plannerID, aPlan = aPlan, unread_messages_count=unread_messages_count, msg = msg))

        elif request.method == 'POST':
            msg = "Please make sure all the required fields are filled out."
            
    except Exception as e:
        flash (str(e), "An error occured while processing your request.")
        print(str(e), "An error occured while processing your request.")
        return redirect (url_for('home.home', aPlan = aPlan))
    
    return render_template('planner/edit_profile.html', plannerID=plannerID, aPlan = aPlan, msg = msg,  unread_messages_count=unread_messages_count)



def is_valid_password(password):
    # check password length
    if len(password) < 8:
        return False
    # check password format
    if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)', password):
        return False
    return True

# Route to allow planner to change password
@pl_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    msg = ''
    planID = current_user.id
    aPlan = Planner.get_plan_info(planID)
    unread_messages_count = get_unread_messages_count(current_user.id)
    if request.method == 'POST':
        if not all(request.form.get(field) for field in ['old_password', 'new_password', 'confirm_new_password']):
            msg = 'Please fill out all the fields.'
        else:
            # Retrieve user input from the form.
            old_password = request.form.get('old_password')
            new_password = request.form.get('new_password')
            confirm_new_password = request.form.get('confirm_new_password')

            # Retrieve the user's current password hash from the database
            current_password_hash = aPlan[11]

            # Check if the old password matches record in database
            if bcrypt.checkpw(old_password.encode('utf-8'), current_password_hash.encode('utf-8')):
        
                # check if password is in valid format
                if not is_valid_password(new_password):
                    msg = 'Password must be at least 8 digit with both letters and numbers.'
                    return render_template('planner/change_password.html', msg=msg, aPlan = aPlan,  unread_messages_count=unread_messages_count)

                # Check if the new password and confirm new password match
                if confirm_new_password == new_password:

                    # Old password matches, proceed to update the password
                    # Hash the new password using bcrypt
                    hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                    # Update the user's password in the database
                    Planner.update_planner_password(hashed_new_password, planID)
                    msg = 'Password updated successfully!'
                    return redirect(url_for('planner.home', aPlan = aPlan, unread_messages_count=unread_messages_count))
                
                else:
                    msg = 'Please confirm, the new passwords do not match'
            
            else:
                # Old password does not match, show an error message
                msg = 'Your old password is incorrect'
                     
    return render_template ('planner/change_password.html',  msg=msg, aPlan = aPlan, unread_messages_count=unread_messages_count)


""" As a planner, I want to be able to view all the bookings, So that I can be aware of the bookings the customer made. 
1. Access 'Booking' from the main dashboard. 
2. An interface displays a list of all bookings, both current and previous. 
3. There's a clear distinction or section where past (historic) bookings are listed. 
4. Each booking entry shows key details such as customer name, venue, date & time, and event type. 
5. Each booking has a status indicator, such as confirmed, pending, cancelled, or completed. 
6. Upon selecting a specific booking, the planner can view detailed information including customer contact details, special requests or notes, payment status, and any associated planners or staff. 
7. There is a button for the planner to view all the bookings assigned to himself/herself  """

@pl_bp.route('/view_bookings', methods=['GET', 'POST'])
@login_required
def view_bookings():
    # get the planer's info
    aPlan = Planner.get_plan_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    historic_bookings = []
    current_bookings = []
    try:
        # get history bookings
        historic_bookings = Planner.view_historic_bookings(current_user.id)
        # get current bookings
        current_bookings = Planner.view_current_bookings(current_user.id)

        # if search function is used
        if request.method == 'POST':
            keyword = request.form['keyword']
            
            if keyword:
                likekeyword = f'%{keyword}%'
                # fecth the searched booking results matching with keyword
                historic_bookings = Planner.search_historic_bookings(current_user.id, likekeyword)
                current_bookings = Planner.search_current_bookings(current_user.id, likekeyword)
                return render_template ('planner/view_all_bookings.html',unread_messages_count=unread_messages_count,  aPlan = aPlan, historic_bookings = historic_bookings, current_bookings = current_bookings)

            else:
                flash('Please enter a keyword')
                
    except Exception as e:
        flash(str(e), "An error occurred while processing your request.")
        print(f"Error: {e}")  
    return render_template ('planner/view_all_bookings.html', unread_messages_count=unread_messages_count, aPlan = aPlan, historic_bookings = historic_bookings, current_bookings = current_bookings)

# fetch a booking by booking id
def get_booking_by_id(booking_id):
    a_booking = BookingService.planner_check_booking_details(booking_id)
    return a_booking

@pl_bp.route('individual_booking_details/<int:booking_id>', methods = ['GET', 'POST'])
@login_required
def individual_booking_details(booking_id):
    # get the planner details 
    aPlan = Planner.get_plan_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    try:
        # get a certain booking details by booking id
        booking = get_booking_by_id(booking_id)
       
        # create a PDF for a certain booking
        if request.method == 'POST':
            if 'export_method' in request.form:
                response = generate_booking_pdf(booking_id)
                return response

    except Exception as e:
        flash(str(e), "An error occurred while processing your request.")
        print(f"Error: {e}")
        return redirect(url_for('planner.view_bookings'))

    return render_template('planner/individual_booking_details.html', booking = booking, aPlan = aPlan, booking_id = booking_id, unread_messages_count=unread_messages_count)


class PDFWithFooter(FPDF):
    def __init__(self, plan_id):
        self.plan_id = plan_id  
        super().__init__()

    def footer(self):
        # Get planner info
        planner = Planner.get_plan_info(self.plan_id)
        # add footer content
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, -20, "Plan It Right Event Management Co.", align='C', ln=True)
        self.cell(0, 10, txt=f"Planner: {planner[1]} - {planner[3]} {planner[4]}", align='C')


def generate_booking_pdf(booking_id):
    booking = get_booking_by_id(booking_id)  # Fetch the bookings from the database
    
    plan_id = current_user.id
    
    pdf = pdf = PDFWithFooter(plan_id)
    pdf.add_page()

    # add a logo
    pdf.image("APP\static\Plan-ItRight.jpg", x=10, y=10, w=50, h=50)

    # title of the PDF
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 60, txt="Booking Details", ln=True, align='C')

    #subtitle
    pdf.set_font("Arial", size=8)
    pdf.cell(200, -40, txt=f"Booking ID: {booking[0]} | | Booking Status: {booking[14]}", ln=True, align='C')
    
    # create a Event Details column
    pdf.set_fill_color(227, 218, 225) # set background colour
    pdf.rect(10, 60, 190, 10, 'F')   # create a rectangle
    pdf.set_text_color(0, 0, 0)  # set text color as black
    pdf.set_font("Arial", size=13)
    pdf.cell(200, 70, txt="Event Details", ln=True, align='C')
    
    pdf.set_font("Arial", size=10)
    pdf.cell(20, -50, txt=f"Booking Start Date and Time: {booking[9].strftime('%d-%m-%Y')} {booking[10]}", ln=True)
    pdf.cell(20, 60, txt=f"Booking End Date and Time: {booking[11].strftime('%d-%m-%Y')} {booking[12]}", ln=True)
    pdf.cell(20, -50, txt=f"Venue Name: {booking[5]}", ln=True)
    pdf.cell(20, 60, txt=f"Venue Location: {booking[6]}", ln=True)
    pdf.cell(20, -50, txt=f"Guest Number: {booking[13]}", ln=True)
    
    # create a Additional Service column
    pdf.set_fill_color(227, 218, 225)  
    pdf.rect(10, 100, 190, 10, 'F') 
    pdf.set_text_color(0, 0, 0)  
    pdf.set_font("Arial", size=13)
    pdf.cell(200, 70, txt="Additional Service", ln=True, align='C')
    
    pdf.set_font("Arial", size=10)
    pdf.cell(20, -50, txt=f"Food Order: {booking[7] or 'N/A'}", ln=True)
    pdf.cell(20, 60, txt=f"Decoration Order: {booking[8] or 'N/A'}", ln=True)
    
    # create a Customer Details column
    pdf.set_fill_color(227, 218, 225)  
    pdf.rect(10, 130, 190, 10, 'F')  
    pdf.set_text_color(0, 0, 0)  
    pdf.set_font("Arial", size=13)
    pdf.cell(200, -30, txt="Customer Details", ln=True, align='C')
    
    pdf.set_font("Arial", size=10)
    pdf.cell(20, 50, txt=f"Customer Name: {booking[2] or 'N/A'}", ln=True)
    pdf.cell(20, -40, txt=f"Phone Number: {booking[3] or 'N/A'}", ln=True)
    pdf.cell(20, 50, txt=f"Email Address: {booking[4] or 'N/A'}", ln=True)
    
    # create a Comments column
    pdf.set_fill_color(227, 218, 225)  
    pdf.rect(10, 160, 190, 10, 'F')  
    pdf.set_text_color(0, 0, 0)  
    pdf.set_font("Arial", size=13)
    pdf.cell(200, -30, txt="Comments", ln=True, align='C')

    pdf.set_font("Arial", size=10)
    pdf.cell(20, 50, txt=f"{booking[15] or 'N/A'}", ln=True)
    
    
    # Add a line to separate bookings
    pdf.ln(10)

    response  = make_response(pdf.output(dest='S').encode('latin1'))
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"inline; filename=Booking_No{booking[0]}.pdf"
    return response



# Route for planner to see all the unassigned bookings
@pl_bp.route('/available/bookings')
@login_required
def view_available_bookings():
    aPlan =  Planner.get_plan_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    available_bookings = None
    today = datetime.now().date()
    try:
        available_bookings = BookingService.planner_view_available_bookings(today)
  
    except Exception as e:
        flash(str(e), "An error occured while processing your request.")

    return render_template('planner/available_bookings.html', available_bookings = available_bookings, aPlan=aPlan, unread_messages_count=unread_messages_count)

#Route for planner to accept a selected booking.
@pl_bp.route('/select-booking/<int:bookingID>', methods=['POST'])
def select_booking(bookingID):
    aPlan =  Planner.get_plan_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    try:
        print("Entered select_booking route")
        print(f"Raw bookingID value: {request.form.get('bookingID')}")
        bookingID = request.form.get('bookingID')
        bookingID = int(bookingID)
        BookingService.planner_accept_booking(current_user.id, bookingID)
        customerID = BookingService.get_customer_id_by_booking(bookingID)
        print(f"customerID: {customerID}")
        associated_venue = BookingService.get_booking_by_id(bookingID)
        venue = associated_venue[18]
        print(f"venue: {venue}")

        today = datetime.today().date()
        NZ_formatted_date = today.strftime("%d-%m-%Y")
        message = f'{NZ_formatted_date} - Your booking at {venue} has been assigned to a planner. Please check your bookings to get more details -- From Planner: {aPlan[0]} {aPlan[3]} {aPlan[4]}'
        print(f"Venue data: {venue}")
        print(message)

        print(f"today: {today}, customerID: {customerID}, current user id: {current_user.id}, message: {message}")

        BookingService.planner_insert_reminder_to_customer(today, customerID, message)

        return redirect(url_for('planner.accepted_bookings', bookingID = bookingID, plannerID = current_user.id, aPlan=aPlan))

    except Exception as e:
        print(f"Exception encountered: {str(e)}")
        flash(str(e), "An error occurred while processing your request.")
        return redirect(url_for('planner.view_available_bookings', bookingID = bookingID, aPlan=aPlan))


#The route for planner to see their own confirmed bookings
@pl_bp.route('/booking/confirmation/<int:plannerID>')
@login_required
def accepted_bookings(plannerID):
    aPlan =  Planner.get_plan_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    try: 
        today = datetime.today()
        current_time = datetime.now().time()
        plannerID= current_user.id
        unread_messages_count = get_unread_messages_count(current_user.id)
        accepted_bookings = BookingService.view_planner_accepted_bookings(plannerID, today, current_time)
    
        quotes = {}
        for booking in accepted_bookings:
            bookingID = booking[13]
            aQuote = Quote.get_quote(bookingID)
            quotes[bookingID] = bool(aQuote)


    except Exception as e:
        flash(str(e), "An error occured while processing your request.")
    
    return render_template('planner/accepted_bookings.html', accepted_bookings=accepted_bookings, aPlan=aPlan, quotes=quotes, unread_messages_count=unread_messages_count)


@pl_bp.route('/mark_as_read/<int:reminderID>', methods=['POST'])
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

def get_unread_messages_count(plannerID):
    try:
        # Get the ID of the currently logged-in planner
        plannerID = current_user.id
        
        # Create an instance of the Notifications class
        unread = Notifications()
        
        # Get the count of unread messages for the planner
        unread_count = unread.unread_message_count_planner(plannerID)

        print("UNREAD MESSAGE COUNT BELOW")
        print(unread_count)

        return unread_count
    except Exception as e:
        # Handle exceptions and display an error flash message
        flash(str(e), "An error occurred while processing your request.")
        print(f"Exception occurred: {str(e)}")

@pl_bp.route('/delete_message/<int:reminderID>', methods=['POST'])
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


@pl_bp.route('/view/messages/<int:plannerID>')
@login_required
def view_messages(plannerID):
    aPlan =  Planner.get_plan_info(current_user.id)
    messages = []
    try:
        notifications = Notifications()  
        all_messages = notifications.planner_view_messages(plannerID)
        unread_messages_count = get_unread_messages_count(current_user.id)
        
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
        return redirect(url_for('planner.home', aPlan = aPlan, error_message=str(e)))  

    return render_template('planner/messagebox.html', aPlan = aPlan, messages=messages,  unread_messages_count=unread_messages_count)

@pl_bp.route('/quote/form/<int:bookingID>', methods=['GET', 'POST'])
@login_required
def quote_form(bookingID):
    try:
        print("Starting quote_form function...")  # Start function
        unread_messages_count = get_unread_messages_count(current_user.id)
        aPlan = Planner.get_plan_info(current_user.id)
        customerID = Customer.get_cust_by_bookingID(bookingID)
        today = datetime.today()
        current_time = datetime.now().time()
        print(f"CustomerID: {customerID}, BookingID: {bookingID}, Today: {today}, Current Time: {current_time}")

        aBooking = BookingService.planner_selected_estimates(bookingID, customerID, today, current_time)
        print(aBooking)
        
        if request.method == 'POST':
            print("Processing POST request...")  # Identify request method
            venue_fee = float(request.form.get('venue_fee', 0))
            decoration_fee = float(request.form.get('decoration_fee', 0))
            menu_price = float(request.form.get('menu_price', 0))
            additional_requirements = request.form.get('additional_requirements')
            additional_fee = float(request.form.get('additional_requirements_fee' , 0))
            discount_percentage = float(request.form.get('discounts', 0)) / 100
            notes = request.form.get('notes')
            expiry_date = request.form.get('expiry_date')
            payment_terms = "100% upfront"

            discount_amount = (venue_fee + decoration_fee + menu_price + additional_fee) * discount_percentage
            total_before_tax = venue_fee + decoration_fee + menu_price + additional_fee - discount_amount
            gst_amount = total_before_tax * 0.15
            total_including_gst = total_before_tax + gst_amount
            print(f"Venue Fee: {venue_fee}, Decoration Fee: {decoration_fee}, Menu Price: {menu_price}, Additional Fee: {additional_fee}")
            print(f"Discount Percentage: {discount_percentage}, Discount Amount: {discount_amount}")

            print(f"Total before tax: {total_before_tax}, GST Amount: {gst_amount}, Total including GST: {total_including_gst}")  # Print calculated values

            quote = Quote(
                bookingID=bookingID,
                venue_fee=venue_fee,
                decor_fee=decoration_fee,
                menu_price=menu_price,
                additional_requirements=additional_requirements,
                additional_fee=additional_fee,
                discounts=discount_amount,
                notes=notes,
                expiry_date=expiry_date,
                payment_terms=payment_terms,
                before_tax=total_before_tax,
                gst_amount=gst_amount,
                total_include_gst=total_including_gst
            )

            Quote.new_quote(quote)
            BookingService.update_status_after_quote(bookingID)
            associated_venue = BookingService.get_booking_by_id(bookingID)
            venue = associated_venue[18]
            print(f'venue: {venue}')
            today = datetime.today().date()
            NZ_formatted_date = today.strftime("%d-%m-%Y")
            message = f'{NZ_formatted_date} - Your quote for booking at {venue} is ready!'
            
            insert_quote_message = Notifications()
            quote_message = insert_quote_message.quote_message(today, customerID, message)

            flash('Quote created successfully!', 'success')
            return redirect(url_for('planner.view_quote', plannerID=current_user.id, aPlan=aPlan, bookingID = bookingID))

    except Exception as e:
        print(f"Error: {e}")  # Print error message
        flash(str(e), "An error occured while processing your request.")
    
    return render_template('planner/quote_form.html', bookingID = bookingID, aBooking=aBooking, aPlan=aPlan,  unread_messages_count=unread_messages_count)


@pl_bp.route('/view/quote/<int:bookingID>', methods=['GET', 'POST'])
@login_required
def view_quote(bookingID):
    try:
        aPlan =  Planner.get_plan_info(current_user.id)
        unread_messages_count = get_unread_messages_count(current_user.id)
        aQuote = Quote.get_quote(bookingID)
        aBooking = BookingService.planner_check_booking_details(bookingID)
        print(aBooking)
        print(aQuote)

        if request.method == 'POST':
            print("Received POST request")
            if 'export_method' in request.form:
                print("Found export_method in form")
                response = generate_quote_pdf(aQuote, aBooking)
                return response

    except Exception as e:
        flash(str(e), "An error occured while processing your request.")
    
    return render_template('planner/view_quote.html', aQuote = aQuote, aBooking=aBooking, aPlan=aPlan, bookingID = bookingID, unread_messages_count=unread_messages_count)


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

  
# As a planner,  I want to be able to edit a booking assigned to me, So that I can make sure the booking information is all correct and updated. 
"""
* Upon selecting a specific booking, the planner edits detailed information including customer contact details, special requests or notes, payment status, and any associated planners or staff. 
* After modifications, there is an option to save changes, and the system updates the booking details immediately. 
* Planner can only edit the booking assigned to himself/herself. """
@pl_bp.route('/edit_booking/<int:booking_id>', methods=['GET','POST'])
@login_required
def edit_booking(booking_id):
    aPlan =  Planner.get_plan_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    booking = BookingService.get_booking_by_id(booking_id)
    venue_order_id = booking[24]
    decor_order_id = booking[5]
    menu_order_id = booking[2]

    venue_list = Venue.get_venue_list() 
    menu_list = BookingService.get_menu_list()
    decoration_list = BookingService.get_decoration_list()

    #Converting time format as apparently HTML does not accept 0:00:00 but 00:00:00 (unsure why missing leading 0 for start time)
    #The zfill(len) method adds zeros (0) at the beginning of the string, until it reaches the specified length which is two in this case.
    booking_start_time = str(booking[9])
    start_time_padded = ':'.join([i.zfill(2) for i in booking_start_time.split(':')])

    booking_end_time = str(booking[11])
    end_time_padded = ':'.join([i.zfill(2) for i in booking_end_time.split(':')])


    if request.method == 'POST':
        # Get start date and end date
        start_date = request.form['start_date']
        end_date = request.form['end_date']

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
        

        venue_id = request.form['venue_id']
        status = request.form['status']
        food_id = request.form['food_id']
        decor_id = request.form.get('decor_id')
        comments = request.form['comments']
        guest = request.form['guest']

        error_messages = []

        # Validate if the guest number is over the venue's max capacity
        selected_venue = Venue.get_venue_by_id(venue_id)
        if int(guest) > selected_venue.get_maxCapacity:
            error_messages.append("The guest number is over the max capacity of the choosen venue, please select another venue.")


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
            
        # Check if Start Date is before today
        today = datetime.today()
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d') 
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')


        # Calculate time difference
        # Covert start and end time as datetime.datetime object, set date as any same day, we only caulculate the time part
        start_datetime = datetime(2023, 1, 1, start_time_object.hour, start_time_object.minute, start_time_object.second)
        end_datetime = datetime(2023, 1, 1, end_time_object.hour, end_time_object.minute, end_time_object.second)

        time_difference = end_datetime - start_datetime
        # Set the minimum time difference is 5 hours
        minimum_time_difference = timedelta(hours=1)

        # Search if the selected date has been taken by other bookings
        booked_venue_date_time = BookingService.find_booked_venue_date_time_by_bookingID(venue_id, booking_id)
        for booked_venue in booked_venue_date_time:
            booked_start = datetime.strptime(booked_venue[0].strftime('%Y-%m-%d'), '%Y-%m-%d')
            booked_end = datetime.strptime(booked_venue[2].strftime('%Y-%m-%d'), '%Y-%m-%d')
            if (start_date_obj >= booked_start and start_date_obj <= booked_end) or (end_date_obj <= booked_end and end_date_obj >= booked_start):
                error_messages.append("Sorry, this venue has been booked during your booking period.")

        # Validate the selected date
        if start_date_obj <= today:
            error_messages.append("The booking date cannot be today or in the past.")
        elif end_date_obj < start_date_obj:
            error_messages.append("The end date cannot be before the start date.")    
        elif (start_date_obj == end_date_obj) and (time_difference < minimum_time_difference):
            error_messages.append("Sorry, the booking period cannot be lower than 1 hour.") 

        # Check if there are any error messages
        if error_messages:
            for message in error_messages:
                flash(message)
            return redirect(url_for('planner.edit_booking', booking_id=booking_id))
        # Update modified information 
        else:
            BookingService.edit_booking(start_date, start_time_sql, end_date, end_time_sql, venue_id, status, guest, comments, booking_id, venue_order_id)
            Planner.planner_edit_customer_profile(booking[14], phone, email)
        
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
        return redirect(url_for('planner.view_bookings', aPlan=aPlan))

    return render_template('planner/edit_booking.html', unread_messages_count=unread_messages_count, aPlan = aPlan, booking_id=booking_id, booking = booking, venue_list = venue_list, decoration_list=decoration_list, menu_list=menu_list, start_time = start_time_padded, end_time = end_time_padded)

# Route for viewing the list of venues
@pl_bp.route('/venue_list')
@login_required
def venue_list():
    aPlan =  Planner.get_plan_info(current_user.id)
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
    #Paginate the venue list
    page = request.args.get('page', 1, type=int)
    per_page = 6

    #Paginate the venue list
    start_index = (page-1)* per_page
    end_index = start_index + per_page

    paginated_venues = venueList[start_index:end_index]
    return render_template('planner/venue_list.html', unread_messages_count=unread_messages_count, aPlan=aPlan, venueList=paginated_venues, page=page, per_page=per_page, sort_column=sort_column, sort_direction=sort_direction, selected_type=selected_type, selected_status=selected_status)

# Route for adding a new venue page
@pl_bp.route('/add_venue', methods=['GET', 'POST'])
@login_required
def add_venue():
    aPlan =  Planner.get_plan_info(current_user.id)
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

        return redirect(url_for('planner.venue_list', aPlan =aPlan ))

    return render_template('planner/add_venue.html', aPlan  = aPlan,  unread_messages_count=unread_messages_count)

# Route for changing the status of a venue
@pl_bp.route('/change_venue_status/<int:venue_id>', methods=['POST'])
def change_venue_status(venue_id):
    venue = Venue.get_venue_by_id(venue_id)
    anPlan = Planner.get_plan_info(current_user.id)
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

    return redirect(url_for('planner.venue_list', anPlan=anPlan))

# Route for editing a venue
@pl_bp.route('/edit_venue/<int:venue_id>', methods=['GET', 'POST'])
def edit_venue(venue_id):
    aPlan = Planner.get_plan_info(current_user.id)
    venue_info = Venue.get_venue_by_id(venue_id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    if request.method == 'GET':
        return render_template('planner/edit_venue.html', venue_info=venue_info, aPlan=aPlan,  unread_messages_count=unread_messages_count)
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
        return redirect(url_for('planner.edit_venue', venue_id=venue_info.get_venueID, aPlan=aPlan))


# Route for deleting an image associated with a venue
@pl_bp.route('/delete_image/<int:venue_id>', methods=['POST'])
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
@pl_bp.route('/add_image/<int:venue_id>', methods=['POST'])
def add_image(venue_id):
    aPlan = Planner.get_plan_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    venue = Venue.get_venue_by_id(venue_id)
    image_urls_text = request.form['image_urls_text']
    if venue and image_urls_text:
        venue.add_image(image_urls_text)
        flash('Image added successfully', 'success')
    else:
        flash('Venue not found or missing image URLs', 'error')

    return redirect(url_for('admin.edit_venue', venue_id=venue_id, aPlan = aPlan,  unread_messages_count =  unread_messages_count))

@pl_bp.route('/menu_list')
def menu_list():
    #get the index for sorting menu List
    sort = request.args.get('sort') 
    menuList = Menu.get_menu_list()
    unread_messages_count = get_unread_messages_count(current_user.id)
    # sort menu List by different trigger
    if sort:
        sort_parts = sort.split('-')
        if len(sort_parts) == 2:
            sort_column, sort_direction = sort_parts
            menuList = Menu.sort_menu_list(menuList, sort_column, sort_direction)

    aPlan = Planner.get_plan_info(current_user.id)

    return render_template('planner/menu_list.html', menuList=menuList, aPlan=aPlan,  unread_messages_count=unread_messages_count)

# Route for adding a new menu page
@pl_bp.route('/add_menu', methods=['GET', 'POST'])
def add_menu():
    aPlan = Planner.get_plan_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    if request.method == 'POST':
        # Retrieve form data for adding a new menu
        menu_name = request.form['menu_name']       
        # Check if the menu with the same name exists
        existing_menu = Menu.get_menu_by_name(menu_name)      
        if existing_menu:
            flash('Menu with this name already exists. Please choose a different name.', 'error')
            return render_template('planner/add_menu.html', aPlan=aPlan,  unread_messages_count=unread_messages_count)
        
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
                return redirect(url_for('planner.menu_list', aPlan=aPlan))
            
            except ValueError as e:
                flash(str(e), 'error')  # Handle validation error
                return render_template('planner/add_menu.html', aPlan=aPlan, unread_messages_count=unread_messages_count)
        
    return render_template('planner/add_menu.html', aPlan=aPlan,  unread_messages_count=unread_messages_count)

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
@pl_bp.route('/edit_menu/<int:menu_id>', methods=['GET', 'POST'])
def edit_menu(menu_id):
    aPlan = Planner.get_plan_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    menu = Menu.get_menu_by_id(menu_id)
    if request.method == 'GET':
        return render_template('planner/edit_menu.html', menu=menu, menu_id=menu_id, aPlan=aPlan, unread_messages_count=unread_messages_count)
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
        return redirect(url_for('planner.edit_menu', menu_id=menu_id, aPlan=aPlan))

# Route for deleting a specific menu
@pl_bp.route('/delete_menu/<int:menu_id>', methods=['GET', 'POST'])
def delete_menu(menu_id):
    aPlan = Planner.get_plan_info(current_user.id)
    menu = Menu.get_menu_by_id(menu_id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    if menu:
        # delete from database
        menu.delete_menu()
        # delete image file
        delete_menu_image_file(menu.image)
        flash('menu deleted successfully!', 'success')
        return redirect(url_for('planner.menu_list', aPlan=aPlan))
    else:
        flash('menu not found!', 'error')
        return redirect(url_for('planner.menu_list', aPlan=aPlan))

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

@pl_bp.route('/delete_menu_image/<int:menu_id>', methods=['POST'])
def delete_menu_image(menu_id):
    aPlan = Planner.get_plan_info(current_user.id)
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

        return redirect(url_for('planner.edit_menu', menu_id=menu_id, aPlan=aPlan))

# Route for adding a new menu image
@pl_bp.route('/add_menu_image/<int:menu_id>', methods=['POST'])
def add_menu_image(menu_id):
    aPlan = Planner.get_plan_info(current_user.id)
    menu = Menu.get_menu_by_id(menu_id)
    unread_messages_count = get_unread_messages_count(current_user.id)

    if request.method == 'POST':
        # Upload file to folder
        new_image = upload_menu_image(app, menu.name)
        # if upload successfully, then update the database
        if new_image:
            # Update the 'image' attribute of the 'menu' object
            menu.update_image(new_image, menu_id)
            flash('Image upload successfully', 'success')
            return redirect(url_for('planner.edit_menu', menu_id=menu_id, aPlan=aPlan))
        
        else:
            flash('Image upload failed', 'error')
            return redirect(url_for('planner.edit_menu', menu_id=menu_id, aPlan=aPlan))


@pl_bp.route('/decoration_list')
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

    aPlan = Planner.get_plan_info(current_user.id)

    return render_template('planner/decoration_list.html', decorationList=decorationList, aPlan=aPlan, unread_messages_count=unread_messages_count)

# Route for adding a new decoration page
@pl_bp.route('/add_decoration', methods=['GET', 'POST'])
def add_decoration():
    aPlan = Planner.get_plan_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)

    if request.method == 'POST':
        # Retrieve form data for adding a new decoration
        decoration_type = request.form['decoration_type']       
        # Check if the decoration with the same name exists
        existing_decoration = Decoration.get_decoration_by_type(decoration_type)      
        if existing_decoration:
            flash('decoration with this name already exists. Please choose a different name.', 'error')
            return render_template('planner/add_decoration.html', aPlan=aPlan, unread_messages_count=unread_messages_count)
        
        price = float(request.form['price'])
        description = request.form['description']

        # upload the image file and return the image name
        decoration_image_name = upload_decoration_image(app, decoration_type)
        
        #if upload successfully then add this decoration into database
        if decoration_image_name:
            try:
                # Attempt to create a new decoration with the provided price
                new_decoration = Decoration(None, decoration_type, price, decoration_image_name, description)
                Decoration.add_decoration(new_decoration)
            
                flash('decoration added successfully!', 'success')
                return redirect(url_for('planner.decoration_list', aPlan=aPlan))
            
            except ValueError as e:
                flash(str(e), 'error')  # Handle validation error
                return render_template('planner/add_decoration.html', aPlan=aPlan, unread_messages_count=unread_messages_count)
        
    return render_template('planner/add_decoration.html', aPlan=aPlan, unread_messages_count=unread_messages_count)

def upload_decoration_image(app, decoration_type):
    if 'decoration_image' in request.files:
        decoration_image = request.files['decoration_image']
        if decoration_image.filename != '':
            # Get the file extension
            file_extension = os.path.splitext(decoration_image.filename)[1].lower()

            # Define a set of allowed file extensions
            allowed_extensions = {'jpg', 'jpeg', 'png', 'gif'}

            if file_extension[1:] not in allowed_extensions:
                flash('Invalid file format. Supported formats: jpg, jpeg, png, gif', 'error')
            else:
                # Ensure the folder exists
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

                # Combine decoration_name with the original file extension
                filename = f"{secure_filename(decoration_type)}{file_extension}"

                # Save the decoration_image file to the folder
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                decoration_image.save(file_path)
                print(f"File saved as: {filename}")

                # Return the file object, not just the name
                return filename  # Return the image name to update database
        else:
            flash('No selected file', 'error')
    
    return None


# Route for editing a decoration
@pl_bp.route('/edit_decoration/<int:decoration_id>', methods=['GET', 'POST'])
def edit_decoration(decoration_id):
    aPlan = Planner.get_plan_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)

    decoration = Decoration.get_decoration_by_id(decoration_id)
    if request.method == 'GET':
        return render_template('planner/edit_decoration.html', decoration=decoration, decoration_id=decoration_id, aPlan=aPlan, unread_messages_count=unread_messages_count)
    if request.method == 'POST':
        # Update decoration's information in the database
        name = request.form['decoration_name']
        price = float(request.form['price'])
        description = request.form['description']

        # Check whether there is a change in any attribute
        attributes_to_update = {
            'name': name,
            'price': price,
            'description': description,
        }
        for attribute, new_value in attributes_to_update.items():
            if new_value != getattr(decoration, f'{attribute}'):
                setattr(decoration, attribute, new_value)

        decoration.update_to_database()

        flash('decoration information updated successfully!', 'success')
        return redirect(url_for('planner.edit_decoration', decoration_id=decoration_id, aPlan=aPlan))

# Route for deleting a specific decoration
@pl_bp.route('/delete_decoration/<int:decoration_id>', methods=['GET', 'POST'])
def delete_decoration(decoration_id):
    aPlan = Planner.get_plan_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    decoration = Decoration.get_decoration_by_id(decoration_id)
    if decoration:
        # delete from database
        decoration.delete_decoration()
        # delete image file
        delete_decoration_image_file(decoration.image)
        flash('decoration deleted successfully!', 'success')
        return redirect(url_for('planner.decoration_list', aPlan=aPlan))
    else:
        flash('decoration not found!', 'error')
        return redirect(url_for('planner.decoration_list', aPlan=aPlan))

def delete_decoration_image_file(image_name):
    try:
        if image_name:
            image_path = os.path.join('APP/static', os.path.basename(image_name))
            if os.path.exists(image_path):
                os.remove(image_path)
                return True
    except Exception as e:
        print(f"Error deleting image: {str(e)}")
    return False

@pl_bp.route('/delete_decoration_image/<int:decoration_id>', methods=['POST'])
def delete_decoration_image(decoration_id):
    aPlan = Planner.get_plan_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)

    if request.method == 'POST':
        decoration = Decoration.get_decoration_by_id(decoration_id)

        if decoration is not None:
            # delete file
            delete_decoration_image_file(decoration.image)
            # delete data
            decoration.delete_image(decoration_id)
            flash('Image deleted successfully!', 'success')
        else:
            flash('decoration not found', 'error')

        return redirect(url_for('planner.edit_decoration', decoration_id=decoration_id, aPlan=aPlan))

# Route for adding a new decoration image
@pl_bp.route('/add_decoration_image/<int:decoration_id>', methods=['POST'])
def add_decoration_image(decoration_id):
    aPlan = Planner.get_plan_info(current_user.id)
    unread_messages_count = get_unread_messages_count(current_user.id)
    decoration = Decoration.get_decoration_by_id(decoration_id)

    if request.method == 'POST':
        # Upload file to folder
        new_image = upload_decoration_image(app, decoration.decor_type)
        # if upload successfully, then update the database
        if new_image:
            # Update the 'image' attribute of the 'decoration' object
            decoration.update_image(new_image, decoration_id)
            flash('Image upload successfully', 'success')
            return redirect(url_for('planner.edit_decoration', decoration_id=decoration_id, aPlan=aPlan))
        
        else:
            flash('Image upload failed', 'error')
            return redirect(url_for('planner.edit_decoration', decoration_id=decoration_id, aPlan=aPlan))


@pl_bp.route('/search/results', methods=['GET', 'POST'])
def search_venue():
    try:
        aPlan = Planner.get_plan_info(current_user.id)
        unread_messages_count = get_unread_messages_count(current_user.id)

        if request.method == 'POST':

            search_query = request.form.get('search_query')
            print(f"Search Query: {search_query}")
            
            venues = Venue.search(search_query)
            print(f"Venues: {venues}") 
            
            if not venues:
                flash('No matching venues found, sorry!')
                return redirect(url_for('planner.venue_list'))
    
    except Exception as e:
        flash(str(e), "An error occured while processing your request.")
        return redirect (url_for('planner.home'))
    
    return render_template ('planner/search_venue_result.html', 
                            aPlan=aPlan,
                            venues = venues, 
                            unread_messages_count=unread_messages_count)

def generate_workload_report_pdf(workload_report_data):
    
    planner_id = current_user.id

    # create PDF footer
    pdf = PDFWithFooter(planner_id)

    # create a new page
    pdf.add_page()

    # add a logo
    pdf.image("APP\static\Plan-ItRight.jpg", x=10, y=10, w=50, h=50)

    # title
    pdf.set_font("Arial", size=20)
    pdf.cell(200, 60, txt="Workload Report", ln=True, align='C')

    # Add header row
    pdf.set_font("Arial", size=13)
    pdf.ln(10)  # optional: add a line break for spacing
    pdf.set_fill_color(227, 218, 225)  # set a fill color for the header row, optional
    pdf.cell(50, 10, txt="Planner Name", fill=True)
    pdf.cell(100, 10, txt="Total Completed Jobs", fill=True)
    pdf.cell(80, 10, txt="Total Guests", fill=True)
    pdf.ln(10)
    
    # Add each data row to the PDF.
    pdf.set_font("Arial", size=13)
    for row in workload_report_data:
        pdf.ln(10)
        pdf.cell(50, 10, txt=str(row[0]))
        pdf.cell(100, 10, txt=str(row[1]))
        pdf.cell(80, 10, txt=str(row[2]))
    
    response = make_response(pdf.output(dest='S').encode('latin1'))
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"inline; filename=workload_report.pdf"
    return response

@pl_bp.route('/report', methods=['GET', 'POST'])
@login_required
def generate_report():
    unread_messages_count = get_unread_messages_count(current_user.id)
    msg = ""
    date_format = "%Y-%m-%d"
    aPlan = Planner.get_plan_info(current_user.id)

    if request.method == 'POST':
        report_type = request.form['report_type']
        starting_date = request.form['starting_date']
        end_date = request.form['end_date']
        
        try:
            start_date_obj = datetime.strptime(starting_date, date_format)
            end_date_obj = datetime.strptime(end_date, date_format)
        except ValueError:
            msg = "Invalid date format. Please use YYYY-MM-DD."
            return render_template('planner/report.html', msg=msg, aPlan = aPlan)
        
        if start_date_obj > end_date_obj:
            msg = "End date must be later than the starting date. Please retry!"
            return render_template('planner/report.html', msg=msg, aPlan = aPlan)

        if report_type == "workload":
            workload_report = Planner.view_workload_report(start_date_obj, end_date_obj, current_user.id)
            if workload_report is not None:
                allStatus_labels = [entry[0] for entry in workload_report]
                allWork_data = [entry[1] for entry in workload_report]

                allStatus_labels_json = json.dumps(allStatus_labels)
                allWork_data_json = json.dumps(allWork_data, default=decimal_default)

                starting_date = datetime.strptime(starting_date, '%Y-%m-%d').strftime('%d-%m-%Y')
                end_date = datetime.strptime(end_date, '%Y-%m-%d').strftime('%d-%m-%Y')
                if 'export_pdf' in request.form:
                    pdf_yes = request.form['export_pdf']
                    if pdf_yes:
                        return generate_workload_report_pdf(workload_report)
        return render_template('planner/get_report.html', aPlan=aPlan, msg=msg,
                                    starting_date=starting_date, end_date=end_date,
                                    workload_report=workload_report,
                                    allStatus_labels_json=allStatus_labels_json,
                                    allWork_data_json=allWork_data_json, unread_messages_count=unread_messages_count)
    return render_template('planner/report.html', msg=msg, aPlan=aPlan, unread_messages_count=unread_messages_count)




def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError
    

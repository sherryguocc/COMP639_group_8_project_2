from APP import getCursor
from datetime import datetime
import uuid
from datetime import datetime, date, time

class BookingService:
    
    # Update venue rented status based on end date
    @staticmethod
    def update_venue_rented_status_based_on_end_date():
        # Get the current date
        today = datetime.now().date()
        connection = getCursor()
        # Update venues that have bookings ending before the current date
        connection.execute("""UPDATE venue
                            JOIN venueorder ON venue.venueID = venueorder.venueID
                            JOIN booking ON venueorder.bookingID = booking.bookingID
                            SET venue.rented = 0
                            WHERE booking.endDate < %s;""", (today,))
    
    # Get the end date of a booking by venue ID
    @staticmethod
    def get_booking_end_date_by_venue_id(venue_id):
        connection = getCursor()
        connection.execute("""SELECT booking.endDate 
                            FROM booking 
                            JOIN venueorder ON booking.bookingID = venueorder.bookingID
                            WHERE venueorder.venueID = %s;""", (venue_id,))
        booking_end_date = connection.fetchone()
        return booking_end_date[0] if booking_end_date else None
    
    # Create a new booking
    @staticmethod
    def create_booking(customer, event_date_db, event_time_db, end_date_db, end_time_db, guest_number, event_details, status):
        connection = getCursor()
        # Insert a new booking into the database
        new_booking = connection.execute("""INSERT INTO booking (customerID, plannerID, venueOrderID, foodOrderID, decorOrderID, startDate, startTime, endDate, endTime, guestsNumber, comments, status)
                                            VALUES (%s, NULL, NULL, NULL, NULL, %s, %s, %s, %s, %s, %s, %s);""" , (customer, event_date_db, event_time_db, end_date_db, end_time_db, guest_number, event_details, status))
        return connection.lastrowid
    
    # Create a venue order
    @staticmethod
    def create_venue_order(venue, booking_id):
        connection = getCursor()
        # Insert a new venue order into the database
        new_venue_order = connection.execute("""INSERT INTO venueorder (venueID, bookingID) VALUES (%s, %s);""", (venue, booking_id))
        return connection.lastrowid
    
    # Create a decoration order
    @staticmethod
    def create_decor_order(booking_id, decoration):
        connection = getCursor()
        connection.execute("""INSERT INTO decororder (bookingID, decorationID) VALUES (%s, %s);""", (booking_id, decoration))
        return connection.lastrowid
    
    # Create a menu order
    @staticmethod
    def create_menu_order(booking_id, food):
        connection = getCursor()
        # Insert a new decoration order into the database
        new_menu_order = connection.execute("""INSERT INTO menuorder (bookingID, foodID) VALUES (%s, %s); """, (booking_id, food))
        return connection.lastrowid

    # Update booking with venue order, menu order, and decor order
    @staticmethod
    def update_booking(booking_id, venueorder_id = None, menu_order_id = None, decor_order_id = None):
        try:
            connection = getCursor()
            columns_to_update = []
            values_to_update = []

            if venueorder_id is not None:
                columns_to_update.append("venueOrderID = %s")
                values_to_update.append(venueorder_id)

            if menu_order_id is not None:
                columns_to_update.append("foodOrderID = %s")
                values_to_update.append(menu_order_id)

            if decor_order_id is not None:
                columns_to_update.append("decorOrderID = %s")
                values_to_update.append(decor_order_id)

            update_booking = f"""UPDATE booking
                        SET {', '.join(columns_to_update)}
                        WHERE bookingID = %s;""" 
            values_to_update.append(booking_id)
            print(update_booking)

            affected_rows = connection.execute(update_booking, tuple(values_to_update))
            print(f"Affected rows: {affected_rows}")
            print(f"Booking ID: {booking_id}, Venue Order ID: {venueorder_id}")
        except Exception as e:
            print(f"Error during update: {e}")

    # Update booking details such as event date, time, guests, and comments
    @staticmethod
    def update_booking_details(booking_id, event_date_db=None, event_time_db=None, end_date_db=None, end_time_db=None, guest_number=None, event_details=None):
        try:
            connection = getCursor()
            columns_to_update = []
            values_to_update = []

            if event_date_db:
                columns_to_update.append("startDate = %s")
                values_to_update.append(event_date_db)

            if event_time_db:
                columns_to_update.append("startTime = %s")
                values_to_update.append(event_time_db)

            if end_date_db:
                columns_to_update.append("endDate = %s")
                values_to_update.append(end_date_db)

            if end_time_db:
                columns_to_update.append("endTime = %s")
                values_to_update.append(end_time_db)

            if guest_number:
                columns_to_update.append("guestsNumber = %s")
                values_to_update.append(guest_number)

            if event_details:
                columns_to_update.append("comments = %s")
                values_to_update.append(event_details)

            query = f"""UPDATE booking
                    SET {', '.join(columns_to_update)}
                    WHERE bookingID = %s;""" 
            values_to_update.append(booking_id)

            affected_rows = connection.execute(query, tuple(values_to_update))
            print(f"Affected rows: {affected_rows}")
        except Exception as e:
            print(f"Error during update: {e}")

     # Get booking details by booking ID
    @staticmethod
    def get_booking_by_id(bookingID):
        connection = getCursor()
        connection.execute("""SELECT venue.location,
                                    venue.venueID,
                                    menuorder.foodOrderID,
                                    menu.name,
                                    menu.foodID,
                                    decororder.decorOrderID,
                                    decoration.decorationType,
                                    decoration.decorationID,
                                    booking.startDate,
                                    booking.startTime,
                                    booking.endDate,
                                    booking.endTime,
                                    booking.guestsNumber,
                                    booking.ref_num,
                                    customer.customerID,
                                    booking.bookingID,
                                    planner.plannerID,
                                    booking.comments,
                                    venue.venueName,
                                    CONCAT(planner.firstName, ' ', planner.lastName) AS plannerName,
                                    CONCAT(customer.firstName, ' ', customer.lastName) AS customerName,
                                    booking.status,
                                    customer.phone,
                                    customer.email,
                                    booking.venueOrderID,
                                    venue.maxCapacity
                                    FROM booking
                                    LEFT JOIN planner ON booking.plannerID = planner.plannerID
                                    LEFT JOIN venueorder ON booking.venueOrderID = venueorder.venueOrderID
                                    LEFT JOIN venue ON venueorder.venueID = venue.venueID
                                    LEFT JOIN menuorder ON booking.foodOrderID = menuorder.foodOrderID
                                    LEFT JOIN menu ON menuorder.foodID = menu.foodID
                                    LEFT JOIN decororder ON booking.decorOrderID = decororder.decorOrderID
                                    LEFT JOIN decoration ON decororder.decorationID = decoration.decorationID
                                    JOIN customer ON booking.customerID = customer.customerID
                                    WHERE booking.bookingID =  %s""", (bookingID,))

        booking_details_by_id = connection.fetchone()
        return booking_details_by_id
    
    # Update venue order with a new venue ID
    @staticmethod
    def update_venue_order(venueID, booking_id):
        connection=getCursor()
        connection.execute("UPDATE venueorder SET venueID = %s WHERE bookingID = %s;", (venueID, booking_id))

    # Delete venue order for a booking
    @staticmethod
    def delete_venue_order(booking_id):
        connection = getCursor()
        connection.execute("DELETE FROM venueorder WHERE bookingID = %s", (booking_id,))

    # Update decoration order with a new decoration ID
    @staticmethod
    def update_decor_order(decorationID, booking_id):
        connection=getCursor()
        connection.execute("UPDATE decororder SET decorationID = %s WHERE bookingID = %s;", (decorationID, booking_id))
        

    # Delete decoration order for a booking
    @staticmethod
    def delete_decor_order(booking_id):
        connection = getCursor()
        connection.execute("UPDATE booking SET decorOrderID = NULL WHERE bookingID = %s", (booking_id,))
        connection.execute("DELETE FROM decororder WHERE bookingID = %s", (booking_id,))
        
    # Update menu order with a new food ID
    @staticmethod
    def update_menu_order(foodID, booking_id):
        connection = getCursor()
        connection.execute("UPDATE menuorder SET foodID = %s WHERE bookingID = %s;", (foodID, booking_id))

    # Delete menu order for a booking
    @staticmethod
    def delete_menu_order(booking_id):
        connection = getCursor()
        connection.execute("UPDATE booking SET foodOrderID = NULL WHERE bookingID = %s", (booking_id,))
        connection.execute("DELETE FROM menuorder WHERE bookingID = %s", (booking_id,))

    # Delete a booking (only if it doesn't have a planner assigned)
    @staticmethod
    def delete_booking(booking_id):
        connection = getCursor()
        connection.execute("""DELETE FROM booking 
                            WHERE bookingID = %s AND plannerID IS NULL""", (booking_id,))

    # Check if a venue is available for a given date range
    @staticmethod
    def is_venue_available(venue_id, start_date, end_date):
        connection = getCursor()
        connection.execute("""SELECT * FROM booking
                                JOIN venueorder ON booking.bookingID = venueorder.bookingID
                                WHERE venueorder.venueID =  %s
                                AND NOT (booking.startDate < %s OR booking.endDate > %s );""",(venue_id, start_date, end_date))
        result = connection.fetchone()
        return result is None
    
    # Retrieve upcoming booking details for a customer
    @staticmethod
    def show_booking_details(customerID, today, current_time):
        connection = getCursor()
        connection.execute ("""SELECT CONCAT(planner.firstName, ' ', planner.lastName) AS plannerName,
                                                    venue.venueName,
                                                    venue.location,
                                                    menuorder.foodOrderID,
                                                    menu.name,
                                                    decororder.decorOrderID,
                                                    decoration.decorationType,
                                                    booking.startDate,
                                                    booking.startTime,
                                                    booking.endDate,
                                                    booking.endTime,
                                                    booking.guestsNumber,
                                                    booking.ref_num,
                                                    customer.customerID,
                                                    COALESCE(decoration.price, 0) AS decoration_price,
                                                    COALESCE(menu.price * booking.guestsNumber, 0) AS menu_price,
                                                    venue.dailyPrice,
                                                    venue.hourlyPrice,
                                                    (FLOOR(TIMESTAMPDIFF(HOUR, CONCAT(booking.startDate, ' ', booking.startTime), CONCAT(booking.endDate, ' ', booking.endTime)) / 24) * venue.dailyPrice) +
													(MOD(TIMESTAMPDIFF(HOUR, CONCAT(booking.startDate, ' ', booking.startTime), CONCAT(booking.endDate, ' ', booking.endTime)), 24) * venue.hourlyPrice) AS venue_price,
                                                    COALESCE(decoration.price, 0) + COALESCE(menu.price * booking.guestsNumber, 0) + 
                                                    (FLOOR(TIMESTAMPDIFF(HOUR, CONCAT(booking.startDate, ' ', booking.startTime), CONCAT(booking.endDate, ' ', booking.endTime)) / 24) * venue.dailyPrice) +
													(MOD(TIMESTAMPDIFF(HOUR, CONCAT(booking.startDate, ' ', booking.startTime), CONCAT(booking.endDate, ' ', booking.endTime)), 24) * venue.hourlyPrice) AS total_estimate,
                                                    booking.bookingID
                                                FROM 
                                                    booking
                                                    LEFT JOIN planner ON booking.plannerID = planner.plannerID
                                                    LEFT JOIN venueorder ON booking.venueOrderID = venueorder.venueOrderID
                                                    LEFT JOIN venue ON venueorder.venueID = venue.venueID
                                                    LEFT JOIN menuorder ON booking.foodOrderID = menuorder.foodOrderID
                                                    LEFT JOIN menu ON menuorder.foodID = menu.foodID
                                                    LEFT JOIN decororder ON booking.decorOrderID = decororder.decorOrderID
                                                    LEFT JOIN decoration ON decororder.decorationID = decoration.decorationID
                                                    JOIN customer ON booking.customerID = customer.customerID
                                                WHERE 
                                                    customer.customerID =  %s
                                                AND (booking.startDate > %s OR (booking.startDate = %s AND booking.startTime > %s))
                                                ORDER BY booking.startDate, booking.startTime;""", (customerID, today, today, current_time))
        upcoming_booking_details = connection.fetchall()
        return upcoming_booking_details
    
    # Retrieve historical booking details for a customer
    @staticmethod
    def show_historical_bookings(customerID, today, current_time):
        connection = getCursor()
        connection.execute ("""SELECT CONCAT(planner.firstName, ' ', planner.lastName) AS plannerName,
                                                    venue.venueName,
                                                    venue.location,
                                                    menuorder.foodOrderID,
                                                    menu.name,
                                                    decororder.decorOrderID,
                                                    decoration.decorationType,
                                                    booking.startDate,
                                                    booking.startTime,
                                                    booking.endDate,
                                                    booking.endTime,
                                                    booking.guestsNumber,
                                                    booking.ref_num,
                                                    customer.customerID,
                                                    COALESCE(decoration.price, 0) AS decoration_price,
                                                    COALESCE(menu.price * booking.guestsNumber, 0) AS menu_price,
                                                    venue.dailyPrice,
                                                    venue.hourlyPrice,
                                                    (FLOOR(TIMESTAMPDIFF(HOUR, CONCAT(booking.startDate, ' ', booking.startTime), CONCAT(booking.endDate, ' ', booking.endTime)) / 24) * venue.dailyPrice) +
													(MOD(TIMESTAMPDIFF(HOUR, CONCAT(booking.startDate, ' ', booking.startTime), CONCAT(booking.endDate, ' ', booking.endTime)), 24) * venue.hourlyPrice) AS venue_price,
                                                    COALESCE(decoration.price, 0) + COALESCE(menu.price * booking.guestsNumber, 0) + 
                                                    (FLOOR(TIMESTAMPDIFF(HOUR, CONCAT(booking.startDate, ' ', booking.startTime), CONCAT(booking.endDate, ' ', booking.endTime)) / 24) * venue.dailyPrice) +
													(MOD(TIMESTAMPDIFF(HOUR, CONCAT(booking.startDate, ' ', booking.startTime), CONCAT(booking.endDate, ' ', booking.endTime)), 24) * venue.hourlyPrice) AS total_estimate,
                                                    booking.bookingID
                                                FROM 
                                                    booking
                                                    LEFT JOIN planner ON booking.plannerID = planner.plannerID
                                                    LEFT JOIN venueorder ON booking.venueOrderID = venueorder.venueOrderID
                                                    LEFT JOIN venue ON venueorder.venueID = venue.venueID
                                                    LEFT JOIN menuorder ON booking.foodOrderID = menuorder.foodOrderID
                                                    LEFT JOIN menu ON menuorder.foodID = menu.foodID
                                                    LEFT JOIN decororder ON booking.decorOrderID = decororder.decorOrderID
                                                    LEFT JOIN decoration ON decororder.decorationID = decoration.decorationID
                                                    JOIN customer ON booking.customerID = customer.customerID
                                                WHERE 
                                                    customer.customerID = %s
                                                AND (booking.startDate < %s OR (booking.startDate = %s AND booking.startTime < %s))
                                                ORDER BY booking.startDate, booking.startTime;""", (customerID, today, today, current_time))
        historical_bookings = connection.fetchall()
        return historical_bookings

    # Create or get a reference number for a booking
    @staticmethod
    def create_or_get_reference_number(booking_id):
        connection = getCursor()
        try:
            # Fetch the existing reference number from the database
            connection.execute("SELECT ref_num FROM booking WHERE bookingID = %s", (booking_id,))
            booking_ref = connection.fetchone()[0]
            if not booking_ref:
                booking_ref = str(uuid.uuid4())
                connection.execute("""UPDATE booking SET ref_num = %s WHERE bookingID = %s;""", (booking_ref, booking_id))

            return booking_ref
        
        except Exception as e:
            print(f"Error: {e}")

    # Retrieve available bookings for a planner
    @staticmethod
    def planner_view_available_bookings(today):
        connection = getCursor()
        connection.execute("""SELECT CONCAT(customer.firstName, ' ', customer.lastName) AS customerName,
                                    customer.customerID,
                                    venue.venueName,
                                    venue.location,
                                    menuorder.foodOrderID,
                                    menu.name,
                                    decororder.decorOrderID,
                                    decoration.decorationType,
                                    booking.startDate,
                                    booking.startTime,
                                    booking.endDate,
                                    booking.endTime,
                                    booking.guestsNumber,
                                    booking.bookingID,
                                    planner.plannerID
                                    FROM booking
                                    LEFT JOIN planner ON booking.plannerID = planner.plannerID
                                    LEFT JOIN venueorder ON booking.venueOrderID = venueorder.venueOrderID
                                    LEFT JOIN venue ON venueorder.venueID = venue.venueID
                                    LEFT JOIN menuorder ON booking.foodOrderID = menuorder.foodOrderID
                                    LEFT JOIN menu ON menuorder.foodID = menu.foodID
                                    LEFT JOIN decororder ON booking.decorOrderID = decororder.decorOrderID
                                    LEFT JOIN decoration ON decororder.decorationID = decoration.decorationID
                                    LEFT JOIN customer ON booking.customerID = customer.customerID 
                                    WHERE booking.plannerID is NULL 
                                    AND booking.status != "Cancelled"
                                    AND booking.startDate > %s""", (today,))
        available_bookings = connection.fetchall()

        return available_bookings
    
    # Accept a booking as a planner
    @staticmethod
    def planner_accept_booking(plannerID, bookingID):
        connection = getCursor()
        connection.execute("""UPDATE booking SET plannerID = %s, status = "Processing" WHERE bookingID =%s;""" , (plannerID, bookingID))
    

    # Get the venue name
    @staticmethod
    def get_venue():
        connection = getCursor()
        venue = connection.execute("""SELECT venue.venueName 
                                         FROM venue 
                                         JOIN venueorder ON venue.venueID = venueorder.venueID
                                         JOIN booking ON venueorder.bookingID = booking.bookingID;""")
        return connection.fetchone()[0]

    # Insert a reminder message 
    @staticmethod
    def planner_insert_reminder_to_customer(today, customerID, notification_message):
        connection = getCursor()
        connection.execute("""INSERT INTO reminder (reminderDate, reminderType, customerID, reminderTxt) 
                                VALUES (%s, 'Individual', %s, %s);""", 
                                (today, customerID, notification_message))

    @staticmethod
    def admin_insert_reminder_to_customer(today, customerID, message):
        connection = getCursor()
        connection.execute("""INSERT INTO reminder (reminderDate, reminderType, customerID, reminderTxt) 
                                VALUES (%s, 'Individual', %s, %s);""", 
                                (today, customerID, message))
    
    @staticmethod
    def admin_insert_reminder_to_planner(today, plannerID, message):
        connection = getCursor()
        connection.execute("""INSERT INTO reminder (reminderDate, reminderType, plannerID, reminderTxt) 
                                VALUES (%s, 'Individual', %s, %s);""", 
                                (today, plannerID, message))
        
    # Customer send enquiry to admin
    @staticmethod
    def customer_insert_reminder_to_admin(today, adminID, message):
        connection = getCursor()
        connection.execute("""INSERT INTO reminder (reminderDate, reminderType,  adminID, reminderTxt) 
                                VALUES (%s, 'Individual',  %s, %s);""", 
                                (today, adminID, message))
    
    # Customer send payment info to planner
    @staticmethod
    def customer_insert_reminder_to_planner(today, plannerID, message):
        connection = getCursor()
        connection.execute("""INSERT INTO reminder (reminderDate, reminderType,  plannerID, reminderTxt) 
                                VALUES (%s, 'Individual',  %s, %s);""", 
                                (today, plannerID, message))
    
    # Guest send enquiry to admin
    @staticmethod
    def guest_insert_reminder(today, guestID, adminID, message):
        connection = getCursor()
        connection.execute("""INSERT INTO reminder (reminderDate, reminderType, guestID, adminID, reminderTxt) 
                                VALUES (%s, 'Individual', %s, %s, %s);""", 
                                (today, guestID, adminID, message))
        

        
    # Guest create an enquiry
    @staticmethod
    def create_guest(title, firstName, lastName, email, enquiry, phone):
        connection = getCursor()
        connection.execute("""INSERT INTO guest (title, firstName, lastName, email, enquery, phone) 
                                VALUES (%s, %s, %s, %s, %s, %s);""", 
                                (title, firstName, lastName, email, enquiry, phone)) 
        return connection.lastrowid      

    # Get the customer ID associated with a booking
    @staticmethod
    def get_customer_id_by_booking(bookingID):
        connection = getCursor()
        connection.execute ("SELECT customerID FROM booking WHERE bookingID = %s;", (bookingID,))
        customerID = connection.fetchone()[0]
        return customerID
    
    # Retrieve planner-accepted bookings
    @staticmethod
    def view_planner_accepted_bookings(plannerID, today, current_time):
        connection = getCursor()
        connection.execute("""
            SELECT 
                CONCAT(customer.firstName, ' ', customer.lastName) AS customerName,
                venue.venueName,
                venue.location,
                menuorder.foodOrderID,
                menu.name,
                decororder.decorOrderID,
                decoration.decorationType,
                booking.startDate,
                booking.startTime,
                booking.endDate,
                booking.endTime,
                booking.guestsNumber,
                planner.plannerID,
                booking.bookingID
            FROM booking
            LEFT JOIN planner ON booking.plannerID = planner.plannerID
            LEFT JOIN venueorder ON booking.venueOrderID = venueorder.venueOrderID
            LEFT JOIN venue ON venueorder.venueID = venue.venueID
            LEFT JOIN menuorder ON booking.foodOrderID = menuorder.foodOrderID
            LEFT JOIN menu ON menuorder.foodID = menu.foodID
            LEFT JOIN decororder ON booking.decorOrderID = decororder.decorOrderID
            LEFT JOIN decoration ON decororder.decorationID = decoration.decorationID
            LEFT JOIN customer ON booking.customerID = customer.customerID 
            WHERE booking.plannerID = %s
            AND (booking.startDate > %s OR (booking.startDate = %s AND booking.startTime > %s))
            ORDER BY booking.startDate, booking.startTime;
            """, (plannerID, today, today, current_time))
        return connection.fetchall()
    
    
    @staticmethod
    def admin_check_booking_details(bookingID):
        connection = getCursor()
        connection.execute("""SELECT b.bookingID, b.customerID, CONCAT(c.firstName, ' ', c.lastName) AS customerName,
                                b.plannerID, CONCAT(p.firstName, ' ', p.lastName) AS plannerName, p.email, p.phone,
                                v.venueName, v.location, m.name, d.decorationType,
                                b.startDate, b.startTime, b.endDate, b.endTime, b.guestsNumber, b.status, c.phone, c.email, b.comments
                                FROM booking b
                                LEFT JOIN planner p ON b.plannerID = p.plannerID
                                LEFT JOIN customer c ON b.customerID = c.customerID
                                LEFT JOIN venueorder vo ON b.venueOrderID = vo.venueOrderID
                                LEFT JOIN venue v ON vo.venueID = v.venueID
                                LEFT JOIN menuorder mo ON b.foodOrderID = mo.foodOrderID
                                LEFT JOIN menu m ON mo.foodID = m.foodID
                                LEFT JOIN decororder deco ON b.decorOrderID = deco.decorOrderID
                                LEFT JOIN decoration d ON deco.decorationID = d.decorationID
                                WHERE b.bookingID = %s;""", (bookingID,))
        a_booking = connection.fetchone()
        return a_booking
    
    @staticmethod
    def planner_check_booking_details(bookingID):
        connection = getCursor()
        connection.execute("""SELECT 
                           b.bookingID, 
                           b.customerID, 
                           CONCAT(c.firstName, ' ', c.lastName) AS customerName, 
                           c.phone, 
                           c.email,
                            v.venueName, 
                           v.location, 
                           m.name, 
                           d.decorationType,
                            b.startDate, 
                           b.startTime, 
                           b.endDate, 
                           b.endTime, 
                           b.guestsNumber, 
                           b.status, 
                           b.comments,
                            c.address,
							CONCAT(p.firstName, ' ', p.lastName) AS plannerName,
                            p.plannerID
                            FROM booking b
                            LEFT JOIN customer c ON b.customerID = c.customerID
                            LEFT JOIN venueorder vo ON b.venueOrderID = vo.venueOrderID
                            LEFT JOIN venue v ON vo.venueID = v.venueID
                            LEFT JOIN menuorder mo ON b.foodOrderID = mo.foodOrderID
                            LEFT JOIN menu m ON mo.foodID = m.foodID
                            LEFT JOIN decororder deco ON b.decorOrderID = deco.decorOrderID
                            LEFT JOIN decoration d ON deco.decorationID = d.decorationID
                            LEFT JOIN planner p ON p.plannerID = b.plannerID
                            WHERE b.bookingID =%s;""", (bookingID,))
        a_booking = connection.fetchone()
        return a_booking


    @staticmethod
    def planner_current_booking_number():

        connection = getCursor()
        connection.execute("""SELECT 
                            p.plannerID, 
                            CONCAT(p.firstName, ' ', p.lastName) AS customerName, 
                            COUNT(b.bookingID) AS bookingCount
                            FROM 
                            planner p
                            LEFT JOIN booking b 
                            ON b.plannerID = p.plannerID AND b.status != 'Completed' AND b.startDate >= CURDATE()
                            GROUP BY 
                            p.plannerID, p.firstName, p.lastName;;
                        """)
        planner_current_bookings = connection.fetchall()
        return planner_current_bookings
    
    @staticmethod
    def search_planner_current_booking_number(keyword):
        connection = getCursor()
        connection.execute("""SELECT p.plannerID, 
                           CONCAT(p.firstName, ' ', p.lastName) AS customerName, 
                           count(bookingID) AS bookingCount
                            FROM planner p
                            LEFT JOIN booking b ON b.plannerID = p.plannerID
                            WHERE p.plannerID LIKE %s OR p.firstName LIKE %s OR p.lastName LIKE %s
                            GROUP BY p.plannerID, p.firstName, p.lastName;""", 
                            (keyword, keyword, keyword))
        planner_current_bookings_result = connection.fetchall()
        return planner_current_bookings_result
        
    @staticmethod
    def get_all_planners():
        connection = getCursor()
        connection.execute("""SELECT * from planner;""")
        planners = connection.fetchall()
        return planners
    
    @staticmethod
    def cancel_booking(booking_id):
        connection = getCursor()
        connection.execute("""UPDATE booking SET status = %s WHERE bookingID =%s;""" , ('Cancelled', booking_id))

    @staticmethod
    def get_menu_list():
        connection = getCursor()
        connection.execute("""SELECT * FROM menu;""")
        menu_list = connection.fetchall()
        return menu_list
    
    @staticmethod
    def get_decoration_list():
        connection = getCursor()
        connection.execute("""SELECT * FROM decoration;""")
        decoration_list = connection.fetchall()
        return decoration_list
    
    @staticmethod
    def edit_booking(start_date, start_time, end_date, end_time, venue_id, status, guest, comments, booking_id, venue_order_id):
        connection=getCursor()
        # Update Venue Order
        connection.execute(
            """UPDATE venueorder SET venueID=%s, bookingID=%s WHERE venueOrderID=%s""",
            (venue_id, booking_id, venue_order_id)
        )
        # Update Booking
        connection.execute(
            """UPDATE booking SET 
            venueOrderID=%s,
            startDate = %s, 
            startTime = %s, 
            endDate=%s, 
            endTime=%s, 
            status=%s,
            guestsNumber=%s, 
            comments=%s 
            WHERE bookingID = %s;""", 
            (venue_order_id, start_date, start_time, end_date, end_time, status, guest, comments, booking_id))

    @staticmethod
    def insert_decor_order(booking_id, new_decor_order_id):
        connection=getCursor()
        connection.execute(
            """UPDATE booking SET decorOrderID=%s WHERE bookingID=%s;""",
            (new_decor_order_id, booking_id)
        )  

    @staticmethod
    def insert_menu_order(booking_id, new_menu_order_id):
        connection=getCursor()
        connection.execute(
            """UPDATE booking SET foodOrderID=%s WHERE bookingID=%s;""",
            (new_menu_order_id, booking_id)
        ) 
        
        
    @staticmethod
    def find_booked_venue_date_time_by_bookingID(venue_id, booking_id):
        connection=getCursor()
        connection.execute(
        """SELECT startDate, startTime, endDate, endTime FROM booking b 
            WHERE b.bookingID = (
            SELECT vo.bookingID FROM pirdb.venueorder vo
            LEFT JOIN booking b ON vo.bookingID = b.bookingID
            WHERE vo.venueID = %s AND b.bookingID != %s AND b.status != 'Cancelled' LIMIT 1);""", (venue_id, booking_id))
        booked_date_time = connection.fetchall()
        return booked_date_time

    
    @staticmethod
    def planner_selected_estimates (bookingID, customerID, today, current_time):
        connection = getCursor()
        connection.execute("""SELECT CONCAT(planner.firstName, ' ', planner.lastName) AS plannerName,
                                                    venue.venueName,
                                                    venue.location,
                                                    menuorder.foodOrderID,
                                                    menu.name,
                                                    decororder.decorOrderID,
                                                    decoration.decorationType,
                                                    booking.startDate,
                                                    booking.startTime,
                                                    booking.endDate,
                                                    booking.endTime,
                                                    booking.guestsNumber,
                                                    booking.ref_num,
                                                    customer.customerID,
                                                    COALESCE(decoration.price, 0) AS decoration_price,
                                                    COALESCE(menu.price * booking.guestsNumber, 0) AS menu_price,
                                                    venue.dailyPrice,
                                                    venue.hourlyPrice,
                                                    (FLOOR(TIMESTAMPDIFF(HOUR, CONCAT(booking.startDate, ' ', booking.startTime), CONCAT(booking.endDate, ' ', booking.endTime)) / 24) * venue.dailyPrice) +
													(MOD(TIMESTAMPDIFF(HOUR, CONCAT(booking.startDate, ' ', booking.startTime), CONCAT(booking.endDate, ' ', booking.endTime)), 24) * venue.hourlyPrice) AS venue_price,
                                                    COALESCE(decoration.price, 0) + COALESCE(menu.price * booking.guestsNumber, 0) + 
                                                    (FLOOR(TIMESTAMPDIFF(HOUR, CONCAT(booking.startDate, ' ', booking.startTime), CONCAT(booking.endDate, ' ', booking.endTime)) / 24) * venue.dailyPrice) +
													(MOD(TIMESTAMPDIFF(HOUR, CONCAT(booking.startDate, ' ', booking.startTime), CONCAT(booking.endDate, ' ', booking.endTime)), 24) * venue.hourlyPrice) AS total_estimate,
                                                    booking.bookingID
                                                FROM 
                                                    booking
                                                    LEFT JOIN planner ON booking.plannerID = planner.plannerID
                                                    LEFT JOIN venueorder ON booking.venueOrderID = venueorder.venueOrderID
                                                    LEFT JOIN venue ON venueorder.venueID = venue.venueID
                                                    LEFT JOIN menuorder ON booking.foodOrderID = menuorder.foodOrderID
                                                    LEFT JOIN menu ON menuorder.foodID = menu.foodID
                                                    LEFT JOIN decororder ON booking.decorOrderID = decororder.decorOrderID
                                                    LEFT JOIN decoration ON decororder.decorationID = decoration.decorationID
                                                    JOIN customer ON booking.customerID = customer.customerID
                                                WHERE 
                                                    customer.customerID = %s AND booking.bookingID =  %s
                                                    AND (booking.startDate > %s OR (booking.startDate = %s AND booking.startTime > %s))
                                                    ORDER BY booking.startDate, booking.startTime;""", (customerID, bookingID, today, today, current_time))
        aBooking_estimates = connection.fetchone()
        return aBooking_estimates

    @staticmethod
    def update_status_after_quote(bookingID):
        connection = getCursor()
        connection.execute("""UPDATE booking SET status = "Waiting for Payment" WHERE bookingID = %s;""", (bookingID,))

    @staticmethod
    def update_status_after_payment(bookingID):
        connection = getCursor()
        connection.execute("""UPDATE booking SET status = "Paid" WHERE bookingID = %s;""", (bookingID,))

    @staticmethod
    def update_status_for_refund(bookingID):
        connection = getCursor()
        connection.execute("""UPDATE booking SET status = "Cancelled" WHERE bookingID = %s;""", (bookingID,))


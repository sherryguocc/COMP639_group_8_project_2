from APP import getCursor

class admin():

    def get_admin_info(adminID):
        connection = getCursor()
        connection.execute("""SELECT * FROM admin WHERE adminID = %s;""", (adminID,))
        adm_user = connection.fetchone()
        return adm_user

    @staticmethod
    def view_historic_bookings():
        connection = getCursor()
        connection.execute("""SELECT b.bookingID, b.customerID, CONCAT(c.firstName, ' ', c.lastName) AS customerName,
								b.plannerID, CONCAT(p.firstName, ' ', p.lastName) AS plannerName, p.email, p.phone,
                                v.venueName, v.location, m.name, d.decorationType,
                                b.startDate, b.startTime, b.endDate, b.endTime, b.guestsNumber, b.status
                                FROM booking b
                                LEFT JOIN planner p ON b.plannerID = p.plannerID
                                LEFT JOIN customer c ON b.customerID = c.customerID
                                LEFT JOIN venueorder vo ON b.venueOrderID = vo.venueOrderID
                                LEFT JOIN venue v ON vo.venueID = v.venueID
                                LEFT JOIN menuorder mo ON b.foodOrderID = mo.foodOrderID
                                LEFT JOIN menu m ON mo.foodID = m.foodID
                                LEFT JOIN decororder deco ON b.decorOrderID = deco.decorOrderID
                                LEFT JOIN decoration d ON deco.decorationID = d.decorationID
                                WHERE b.endDate < CURDATE() 
                                ORDER BY b.startDate DESC, b.startTime;""")
        bookings = connection.fetchall()
        return bookings
    
    @staticmethod
    def view_current_bookings():
        connection = getCursor()
        connection.execute("""SELECT b.bookingID, b.customerID, CONCAT(c.firstName, ' ', c.lastName) AS customerName,
								b.plannerID, CONCAT(p.firstName, ' ', p.lastName) AS plannerName, p.email, p.phone,
                                v.venueName, v.location, m.name, d.decorationType,
                                b.startDate, b.startTime, b.endDate, b.endTime, b.guestsNumber, b.status
                                FROM booking b
                                LEFT JOIN planner p ON b.plannerID = p.plannerID
                                LEFT JOIN customer c ON b.customerID = c.customerID
                                LEFT JOIN venueorder vo ON b.venueOrderID = vo.venueOrderID
                                LEFT JOIN venue v ON vo.venueID = v.venueID
                                LEFT JOIN menuorder mo ON b.foodOrderID = mo.foodOrderID
                                LEFT JOIN menu m ON mo.foodID = m.foodID
                                LEFT JOIN decororder deco ON b.decorOrderID = deco.decorOrderID
                                LEFT JOIN decoration d ON deco.decorationID = d.decorationID
                                WHERE b.endDate >= CURDATE() 
                                ORDER BY b.startDate, b.startTime;""")
        bookings = connection.fetchall()
        return bookings
    
    @staticmethod
    def search_bookings(keyword):
        connection = getCursor()
        connection.execute("""SELECT b.bookingID, b.customerID, CONCAT(c.firstName, ' ', c.lastName) AS customerName,
								b.plannerID, CONCAT(p.firstName, ' ', p.lastName) AS plannerName, p.email, p.phone,
                                v.venueName, v.location, m.name, d.decorationType,
                                b.startDate, b.startTime, b.endDate, b.endTime, b.guestsNumber, b.status
                                FROM booking b
                                LEFT JOIN planner p ON b.plannerID = p.plannerID
                                LEFT JOIN customer c ON b.customerID = c.customerID
                                LEFT JOIN venueorder vo ON b.venueOrderID = vo.venueOrderID
                                LEFT JOIN venue v ON vo.venueID = v.venueID
                                LEFT JOIN menuorder mo ON b.foodOrderID = mo.foodOrderID
                                LEFT JOIN menu m ON mo.foodID = m.foodID
                                LEFT JOIN decororder deco ON b.decorOrderID = deco.decorOrderID
                                LEFT JOIN decoration d ON deco.decorationID = d.decorationID
                                WHERE c.firstName = %s OR c.lastName = %s OR p.firstName =%s OR p.lastName = %s OR v.venueName = %s OR b.startDate = %s OR b.endDate = %s OR b.status = %s
                                ORDER BY b.startDate, b.startTime;""", 
                                (keyword, keyword, keyword, keyword, keyword, keyword, keyword, keyword))
        bookings = connection.fetchall()
        return bookings
    
    @staticmethod
    def search_history_bookings(keyword):
        connection = getCursor()
        connection.execute("""SELECT 
                                b.bookingID, 
                                b.customerID, 
                                CONCAT(c.firstName, ' ', c.lastName) AS customerName,
                                b.plannerID, 
                                CONCAT(p.firstName, ' ', p.lastName) AS plannerName, 
                                p.email, 
                                p.phone,   
                                v.venueName, 
                                v.location, 
                                m.name, 
                                d.decorationType, 
                                b.startDate, 
                                b.startTime, 
                                b.endDate, 
                                b.endTime, 
                                b.guestsNumber, 
                                b.status
                                FROM booking b
                                LEFT JOIN planner p ON b.plannerID = p.plannerID
                                LEFT JOIN customer c ON b.customerID = c.customerID
                                LEFT JOIN venueorder vo ON b.venueOrderID = vo.venueOrderID
                                LEFT JOIN venue v ON vo.venueID = v.venueID
                                LEFT JOIN menuorder mo ON b.foodOrderID = mo.foodOrderID
                                LEFT JOIN menu m ON mo.foodID = m.foodID
                                LEFT JOIN decororder deco ON b.decorOrderID = deco.decorOrderID
                                LEFT JOIN decoration d ON deco.decorationID = d.decorationID
                                WHERE (c.firstName LIKE %s OR c.lastName LIKE %s OR p.firstName LIKE %s OR p.lastName LIKE %s OR v.venueName LIKE %s OR b.startDate LIKE %s OR b.endDate LIKE %s OR b.status LIKE %s) and (b.endDate < CURDATE() )                               ORDER BY b.startDate, b.startTime;""", 
                                (keyword, keyword, keyword, keyword, keyword, keyword, keyword, keyword))
        history_bookings_results = connection.fetchall()
        return history_bookings_results
    
    @staticmethod
    def search_current_bookings(keyword):
        connection = getCursor()
        connection.execute("""SELECT 
                                b.bookingID, 
                                b.customerID, 
                                CONCAT(c.firstName, ' ', c.lastName) AS customerName,
                                b.plannerID, 
                                CONCAT(p.firstName, ' ', p.lastName) AS plannerName, 
                                p.email, 
                                p.phone,   
                                v.venueName, 
                                v.location, 
                                m.name, 
                                d.decorationType, 
                                b.startDate, 
                                b.startTime, 
                                b.endDate, 
                                b.endTime, 
                                b.guestsNumber, 
                                b.status
                                FROM booking b
                                LEFT JOIN planner p ON b.plannerID = p.plannerID
                                LEFT JOIN customer c ON b.customerID = c.customerID
                                LEFT JOIN venueorder vo ON b.venueOrderID = vo.venueOrderID
                                LEFT JOIN venue v ON vo.venueID = v.venueID
                                LEFT JOIN menuorder mo ON b.foodOrderID = mo.foodOrderID
                                LEFT JOIN menu m ON mo.foodID = m.foodID
                                LEFT JOIN decororder deco ON b.decorOrderID = deco.decorOrderID
                                LEFT JOIN decoration d ON deco.decorationID = d.decorationID
                                WHERE (c.firstName LIKE %s OR c.lastName LIKE %s OR p.firstName LIKE %s OR p.lastName LIKE %s OR v.venueName LIKE %s OR b.startDate LIKE %s OR b.endDate LIKE %s OR b.status LIKE %s) and (b.endDate >= CURDATE() )                               ORDER BY b.startDate, b.startTime;""", 
                                (keyword, keyword, keyword, keyword, keyword, keyword, keyword, keyword))
        current_bookings_results = connection.fetchall()
        return current_bookings_results
    
    @staticmethod
    def update_admin_profile():
        pass
    
    @staticmethod
    def add_customer(user_no, title, first_name, last_name, email, hashedp):
        connection = getCursor()
        connection.execute('''INSERT INTO customer (userNo, title, firstName, lastName, position, email, PasswordHash) VALUES (%s, %s, %s, %s,'customer', %s, %s);''', 
                          (user_no, title, first_name, last_name, email, hashedp))
        
    @staticmethod 
    def update_customer_profile(title, firstName, lastName, phone, email, address, dob, custID):
        connection = getCursor()
        connection.execute("""UPDATE customer SET title = %s, firstName = %s, lastName = %s, phone = %s, email = %s, address = %s, DOB = %s WHERE customerID = %s;""", (title, firstName, lastName, phone, email, address, dob, custID))    
    
    @staticmethod
    def delete_customer(custID):
        connection = getCursor()
        connection.execute('DELETE FROM customer WHERE customerID = %s;', (custID,))

    @staticmethod
    def admin_send_message_cust (customer_id, message_date, message, message_image, adminID):
        connection = getCursor()
        connection.execute('''INSERT INTO reminder (reminderDate, reminderType, customerID, adminID, reminderTxt, reminderImg) VALUES (%s, 'Individual', %s, %s, %s, %s);''', (message_date, customer_id, adminID, message, message_image))

    @staticmethod
    def update_admin_profile(Title, FirstName, LastName, Phone, Email, adminID):
        connection = getCursor()
        connection.execute("""UPDATE admin SET 
                                title = %s, firstName = %s, lastName = %s, phone = %s, email = %s WHERE adminID = %s;""",
                           (Title, FirstName, LastName, Phone, Email, adminID))
    
    @staticmethod
    def update_admin_password(hashed_new_password, adminID):
        connection = getCursor()
        update_query = "UPDATE admin SET password = %s WHERE adminID = %s"
        connection.execute(update_query, (hashed_new_password, adminID))

    @staticmethod
    def add_planner(user_no, title, first_name, last_name, email, hashed_password):
        connection = getCursor()
        connection.execute('''INSERT INTO planner (userNo, title, firstName, lastName, position, email, Password) VALUES (%s, %s, %s, %s,'planner', %s, %s);''',
                           (user_no, title, first_name, last_name, email, hashed_password))
        
    @staticmethod
    def delete_planner_by_id(planner_id):
        connection = getCursor()
        connection.execute('DELETE FROM planner WHERE plannerID = %s;', (planner_id,))

    @staticmethod
    def update_planner(title, firstName, lastName, phone, email, address, profile, profile_pic, plan_id):
        connection = getCursor()
        connection.execute('''UPDATE planner SET title = %s, firstName = %s, lastName = %s, phone = %s, email = %s, address = %s, profileDescription = %s, profilePhoto = %s WHERE plannerID = %s;''', 
                           (title, firstName, lastName, phone, email, address, profile, profile_pic, plan_id))
        
    @staticmethod
    def admin_edit_customer_profile(customerID, Phone, Email):
        try:
            connection = getCursor()
            connection.execute("""UPDATE customer SET 
                        phone = %s, email = %s WHERE customerID = %s;""",
                        (Phone, Email, customerID))

        except Exception as e:
            print(f"Error while updating profile: {str(e)}")

    @staticmethod
    def view_revenue_report(status, starting_date, end_date):
        connection = getCursor()
        connection.execute("""SELECT vo.venueID, v.venueName, SUM(p.amount) AS total_amount
                        FROM booking b
                        LEFT JOIN payment p ON b.bookingID = p.bookingID
                        LEFT JOIN venueorder vo ON b.venueOrderID = vo.venueOrderID
                        LEFT JOIN venue v ON vo.venueID = v.venueID
                        WHERE b.status = %s
                            AND b.startDate >= %s 
                            AND b.endDate <= %s
                        GROUP BY vo.venueID, v.venueName;""", (status, starting_date, end_date))
        report = connection.fetchall()
        return report

        
    @staticmethod
    def view_popularity_report(starting_date, end_date):
        connection = getCursor()
        connection.execute("""SELECT v.venueID, v.venueName,
                            COUNT(b.bookingID) AS numBookings,
                            (COUNT(b.bookingID) / (SELECT COUNT(*) FROM booking)) * 100 AS percentageOfTotal,
                            AVG(p.amount) AS avgRevenue FROM venue v
                            LEFT JOIN venueorder vo ON v.venueID = vo.venueID
                            LEFT JOIN booking b ON b.venueOrderID = vo.venueOrderID
                            LEFT JOIN payment p ON b.bookingID = p.bookingID
                            WHERE b.startDate >= %s AND b.endDate <= %s
                            GROUP BY v.venueID;""", (starting_date, end_date))
        report = connection.fetchall()
        return report
        
    @staticmethod
    def view_historic_bookings_cust(customer_id):
        connection = getCursor()
        connection.execute("""SELECT b.bookingID, b.customerID, CONCAT(p.firstName, ' ', p.lastName) AS plannerName,
                                v.venueName, v.location, m.name, d.decorationType,
                                b.startDate, b.startTime, b.endDate, b.endTime, b.guestsNumber, b.status,
                                CONCAT(p.firstName, ' ', p.lastName) AS plannerName
                                FROM booking b
                                LEFT JOIN customer c ON b.customerID = c.customerID
                                LEFT JOIN planner p ON b.plannerID = p.plannerID
                                LEFT JOIN venueorder vo ON b.venueOrderID = vo.venueOrderID
                                LEFT JOIN venue v ON vo.venueID = v.venueID
                                LEFT JOIN menuorder mo ON b.foodOrderID = mo.foodOrderID
                                LEFT JOIN menu m ON mo.foodID = m.foodID
                                LEFT JOIN decororder deco ON b.decorOrderID = deco.decorOrderID
                                LEFT JOIN decoration d ON deco.decorationID = d.decorationID
                                WHERE b.customerID = %s AND b.endDate < CURDATE() 
                                ORDER BY b.startDate, b.startTime DESC;""", (customer_id,))
        bookings = connection.fetchall()
        return bookings

    @staticmethod
    def view_current_bookings_cust(customer_id):
        connection = getCursor()
        connection.execute("""SELECT b.bookingID, b.customerID, CONCAT(p.firstName, ' ', p.lastName) AS plannerName,
                                v.venueName, v.location, m.name, d.decorationType,
                                b.startDate, b.startTime, b.endDate, b.endTime, b.guestsNumber, b.status,
                                CONCAT(p.firstName, ' ', p.lastName) AS plannerName
                                FROM booking b
                                LEFT JOIN customer c ON b.customerID = c.customerID
                                LEFT JOIN planner p ON b.plannerID = p.plannerID
                                LEFT JOIN venueorder vo ON b.venueOrderID = vo.venueOrderID
                                LEFT JOIN venue v ON vo.venueID = v.venueID
                                LEFT JOIN menuorder mo ON b.foodOrderID = mo.foodOrderID
                                LEFT JOIN menu m ON mo.foodID = m.foodID
                                LEFT JOIN decororder deco ON b.decorOrderID = deco.decorOrderID
                                LEFT JOIN decoration d ON deco.decorationID = d.decorationID
                                WHERE b.customerID = %s AND b.endDate >= CURDATE() 
                                ORDER BY b.startDate, b.startTime;""", (customer_id,))
        bookings = connection.fetchall()
        return bookings
    
    @staticmethod
    def search_historic_bookings_cust(customer_id, keyword):
        connection = getCursor()
        connection.execute("""SELECT b.bookingID, b.customerID, CONCAT(p.firstName, ' ', p.lastName) AS plannerName,
                                v.venueName, v.location, m.name, d.decorationType,
                                b.startDate, b.startTime, b.endDate, b.endTime, b.guestsNumber, b.status
                                FROM booking b
                                LEFT JOIN customer c ON b.customerID = c.customerID
                                LEFT JOIN venueorder vo ON b.venueOrderID = vo.venueOrderID
                                LEFT JOIN venue v ON vo.venueID = v.venueID
                                LEFT JOIN menuorder mo ON b.foodOrderID = mo.foodOrderID
                                LEFT JOIN menu m ON mo.foodID = m.foodID
                                LEFT JOIN decororder deco ON b.decorOrderID = deco.decorOrderID
                                LEFT JOIN decoration d ON deco.decorationID = d.decorationID
                                WHERE b.customerID = %s AND (c.firstName LIKE %s OR c.lastName LIKE %s OR v.venueName LIKE %s OR b.startDate LIKE %s OR b.endDate LIKE %s OR b.status LIKE %s) AND b.endDate < CURDATE()
                                ORDER BY b.startDate, b.startTime DESC;""", 
                                (customer_id, keyword, keyword, keyword, keyword, keyword, keyword))
        historic_bookings_results = connection.fetchall()
        return historic_bookings_results
    
    @staticmethod
    def search_current_bookings_cust(customer_id, keyword):
        connection = getCursor()
        connection.execute("""SELECT b.bookingID, b.customerID, CONCAT(p.firstName, ' ', p.lastName) AS plannerName,
                                v.venueName, v.location, m.name, d.decorationType,
                                b.startDate, b.startTime, b.endDate, b.endTime, b.guestsNumber, b.status
                                FROM booking b
                                LEFT JOIN customer c ON b.customerID = c.customerID
                                LEFT JOIN venueorder vo ON b.venueOrderID = vo.venueOrderID
                                LEFT JOIN venue v ON vo.venueID = v.venueID
                                LEFT JOIN menuorder mo ON b.foodOrderID = mo.foodOrderID
                                LEFT JOIN menu m ON mo.foodID = m.foodID
                                LEFT JOIN decororder deco ON b.decorOrderID = deco.decorOrderID
                                LEFT JOIN decoration d ON deco.decorationID = d.decorationID
                                WHERE b.customerID = %s AND (c.firstName LIKE %s OR c.lastName LIKE %s OR v.venueName LIKE %s OR b.startDate LIKE %s OR b.endDate LIKE %s OR b.status LIKE %s) AND b.endDate >= CURDATE()
                                ORDER BY b.startDate ASC, b.startTime ASC;""", 
                                (customer_id, keyword, keyword, keyword, keyword, keyword, keyword))
        current_bookings_results = connection.fetchall()
        return current_bookings_results
    
    @staticmethod
    def view_historic_bookings_plan(plan_id):
        connection = getCursor()
        connection.execute("""SELECT b.bookingID, b.customerID, CONCAT(c.firstName, ' ', c.lastName) AS customerName,
                                v.venueName, v.location, m.name, d.decorationType,
                                b.startDate, b.startTime, b.endDate, b.endTime, b.guestsNumber, b.status,
                                CONCAT(p.firstName, ' ', p.lastName) AS plannerName
                                FROM booking b
                                LEFT JOIN customer c ON b.customerID = c.customerID
                                LEFT JOIN planner p ON b.plannerID = p.plannerID
                                LEFT JOIN venueorder vo ON b.venueOrderID = vo.venueOrderID
                                LEFT JOIN venue v ON vo.venueID = v.venueID
                                LEFT JOIN menuorder mo ON b.foodOrderID = mo.foodOrderID
                                LEFT JOIN menu m ON mo.foodID = m.foodID
                                LEFT JOIN decororder deco ON b.decorOrderID = deco.decorOrderID
                                LEFT JOIN decoration d ON deco.decorationID = d.decorationID
                                WHERE b.plannerID = %s AND b.endDate < CURDATE() 
                                ORDER BY b.startDate, b.startTime DESC;""", (plan_id,))
        bookings = connection.fetchall()
        return bookings

    @staticmethod
    def view_current_bookings_plan(plan_id):
        connection = getCursor()
        connection.execute("""SELECT b.bookingID, b.customerID, CONCAT(c.firstName, ' ', c.lastName) AS customerName,
                                v.venueName, v.location, m.name, d.decorationType,
                                b.startDate, b.startTime, b.endDate, b.endTime, b.guestsNumber, b.status,
                                CONCAT(p.firstName, ' ', p.lastName) AS plannerName
                                FROM booking b
                                LEFT JOIN customer c ON b.customerID = c.customerID
                                LEFT JOIN planner p ON b.plannerID = p.plannerID
                                LEFT JOIN venueorder vo ON b.venueOrderID = vo.venueOrderID
                                LEFT JOIN venue v ON vo.venueID = v.venueID
                                LEFT JOIN menuorder mo ON b.foodOrderID = mo.foodOrderID
                                LEFT JOIN menu m ON mo.foodID = m.foodID
                                LEFT JOIN decororder deco ON b.decorOrderID = deco.decorOrderID
                                LEFT JOIN decoration d ON deco.decorationID = d.decorationID
                                WHERE b.plannerID = %s AND b.endDate >= CURDATE() 
                                ORDER BY b.startDate, b.startTime;""", (plan_id,))
        bookings = connection.fetchall()
        return bookings
    
    @staticmethod
    def search_historic_bookings_plan(plan_id, keyword):
        connection = getCursor()
        connection.execute("""SELECT b.bookingID, b.customerID, CONCAT(c.firstName, ' ', c.lastName) AS customerName,
                                v.venueName, v.location, m.name, d.decorationType,
                                b.startDate, b.startTime, b.endDate, b.endTime, b.guestsNumber, b.status
                                FROM booking b
                                LEFT JOIN customer c ON b.customerID = c.customerID
                                LEFT JOIN planner p ON b.plannerID = p.plannerID
                                LEFT JOIN venueorder vo ON b.venueOrderID = vo.venueOrderID
                                LEFT JOIN venue v ON vo.venueID = v.venueID
                                LEFT JOIN menuorder mo ON b.foodOrderID = mo.foodOrderID
                                LEFT JOIN menu m ON mo.foodID = m.foodID
                                LEFT JOIN decororder deco ON b.decorOrderID = deco.decorOrderID
                                LEFT JOIN decoration d ON deco.decorationID = d.decorationID
                                WHERE b.plannerID = %s AND (c.firstName LIKE %s OR c.lastName LIKE %s OR v.venueName LIKE %s OR b.startDate LIKE %s OR b.endDate LIKE %s OR b.status LIKE %s) AND b.endDate < CURDATE()
                                ORDER BY b.startDate, b.startTime DESC;""", 
                                (plan_id, keyword, keyword, keyword, keyword, keyword, keyword))
        historic_bookings_results = connection.fetchall()
        return historic_bookings_results
    
    @staticmethod
    def search_current_bookings_plan(plan_id, keyword):
        connection = getCursor()
        connection.execute("""SELECT b.bookingID, b.customerID, CONCAT(c.firstName, ' ', c.lastName) AS customerName,
                                v.venueName, v.location, m.name, d.decorationType,
                                b.startDate, b.startTime, b.endDate, b.endTime, b.guestsNumber, b.status
                                FROM booking b
                                LEFT JOIN customer c ON b.customerID = c.customerID
                                LEFT JOIN planner p ON b.plannerID = p.plannerID
                                LEFT JOIN venueorder vo ON b.venueOrderID = vo.venueOrderID
                                LEFT JOIN venue v ON vo.venueID = v.venueID
                                LEFT JOIN menuorder mo ON b.foodOrderID = mo.foodOrderID
                                LEFT JOIN menu m ON mo.foodID = m.foodID
                                LEFT JOIN decororder deco ON b.decorOrderID = deco.decorOrderID
                                LEFT JOIN decoration d ON deco.decorationID = d.decorationID
                                WHERE b.plannerID = %s AND (c.firstName LIKE %s OR c.lastName LIKE %s OR v.venueName LIKE %s OR b.startDate LIKE %s OR b.endDate LIKE %s OR b.status LIKE %s) AND b.endDate >= CURDATE()
                                ORDER BY b.startDate ASC, b.startTime ASC;""", 
                                (plan_id, keyword, keyword, keyword, keyword, keyword, keyword))
        current_bookings_results = connection.fetchall()
        return current_bookings_results
    
    @staticmethod
    def view_payment_details(booking_id):
        connection = getCursor()
        connection.execute("""SELECT b.bookingID, p.amount, p.bankAccount, p.paymentDate, b.status, p.paymentID
                                FROM booking b
                                LEFT JOIN customer c ON b.customerID = c.customerID
                                LEFT JOIN payment p ON p.bookingID = b.bookingID
                                WHERE b.bookingID = %s
                                ORDER BY p.paymentDate ASC;""", (booking_id,))
        payment_details = connection.fetchone()
        return payment_details
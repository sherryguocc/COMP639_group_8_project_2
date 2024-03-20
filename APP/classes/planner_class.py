from APP import getCursor

class Planner():

    @staticmethod
    def get_all_planners():
        connection = getCursor()
        connection.execute('SELECT * FROM planner')
        return connection.fetchall()
    
    @staticmethod
    def get_plan_info(planID):
        connection = getCursor()
        connection.execute("""SELECT * FROM planner WHERE plannerID = %s;""", (planID,))
        plan_user = connection.fetchone()
        return plan_user

    @staticmethod
    def search_historic_bookings(plan_id, keyword):
        connection = getCursor()
        connection.execute("""SELECT b.bookingID, b.customerID, CONCAT(c.firstName, ' ', c.lastName) AS customerName,
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
                                WHERE b.plannerID = %s AND (c.firstName LIKE %s OR c.lastName LIKE %s OR v.venueName LIKE %s OR b.startDate LIKE %s OR b.endDate LIKE %s OR b.status LIKE %s) AND b.endDate < CURDATE()
                                ORDER BY b.startDate, b.startTime DESC;""", 
                                (plan_id, keyword, keyword, keyword, keyword, keyword, keyword))
        historic_bookings_results = connection.fetchall()
        return historic_bookings_results
    
    @staticmethod
    def search_current_bookings(plan_id, keyword):
        connection = getCursor()
        connection.execute("""SELECT b.bookingID, b.customerID, CONCAT(c.firstName, ' ', c.lastName) AS customerName,
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
                                WHERE b.plannerID = %s AND (c.firstName LIKE %s OR c.lastName LIKE %s OR v.venueName LIKE %s OR b.startDate LIKE %s OR b.endDate LIKE %s OR b.status LIKE %s) AND b.endDate >= CURDATE()
                                ORDER BY b.startDate ASC, b.startTime ASC;""", 
                                (plan_id, keyword, keyword, keyword, keyword, keyword, keyword))
        current_bookings_results = connection.fetchall()
        return current_bookings_results
    
    @staticmethod
    def view_historic_bookings(plan_id):
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
    def view_current_bookings(plan_id):
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
    def search_planner(query):
        connection = getCursor()
        connection.execute('SELECT * FROM planner WHERE firstName LIKE %s OR lastName LIKE %s OR email LIKE %s OR address LIKE %s;', ('%' + query + '%', '%' + query + '%', '%' + query + '%', '%' + query + '%'))
        return connection.fetchall()

    @staticmethod
    def get_planner_by_email(email):
        connection = getCursor()
        connection.execute("""SELECT email FROM planner WHERE email = %s;""", (email,))
        return connection.fetchone()

    @staticmethod
    def update_planner(Title, FirstName, LastName, Phone, Email, Address, Description, Photo, planID):
        try:
            connection = getCursor()
            connection.execute("""UPDATE planner SET 
                        title = %s, firstName = %s, lastName = %s, phone = %s, email = %s, address = %s, profileDescription = %s, profilePhoto = %s  WHERE plannerID = %s;""",
                               (Title, FirstName, LastName, Phone, Email, Address, Description, Photo, planID))
            return True
        except Exception as e:
            print("Error in updating planner:", e)
            return False
        
    @staticmethod
    def update_planner_password(hashed_new_password, plannerID):
        connection = getCursor()
        connection.execute("UPDATE planner SET Password = %s WHERE plannerID = %s;", (hashed_new_password, plannerID)) 

    @staticmethod
    def planner_edit_customer_profile(customerID, Phone, Email):
        try:
            connection = getCursor()
            connection.execute("""UPDATE customer SET 
                        phone = %s, email = %s WHERE customerID = %s;""",
                        (Phone, Email, customerID))

        except Exception as e:
            print(f"Error while updating profile: {str(e)}")

    @staticmethod
    def view_workload_report(starting_date, end_date, planner_id):
        connection = getCursor()
        connection.execute("""SELECT CONCAT(p.firstName,' ',p.lastName) AS plannerName,
                            COUNT(p.plannerID) as Workload,
                            SUM(b.guestsNumber) AS Totalguest 
                            FROM booking b
                            JOIN planner p ON b.plannerID = p.plannerID
                            WHERE b.startDate >= %s AND b.endDate <= %s AND b.status = "Completed" AND p.plannerID = %s
                            GROUP BY p.plannerID = %s""", (starting_date, end_date, planner_id, planner_id ))
        report = connection.fetchall()
        return report

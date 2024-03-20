from APP import getCursor

class Notifications:
    def __init__ (self):
        # Initialize the Notifications class with a database connection.
        self.__connection = getCursor()
    

    @property
    def connection(self):
        return self.__connection
    
    def customer_view_messages(self, customerID):
        # Retrieve messages for a specific customer.
        self.__connection.execute ("""SELECT CONCAT(customer.firstName, ' ', customer.lastName) AS customerName,
                                                CONCAT(planner.firstName, ' ', planner.lastName) AS plannerName,
                                                CONCAT(admin.firstName, ' ', admin.lastName) AS adminName,
                                                CONCAT(guest.firstName, ' ',guest.lastName) AS guestName,
                                                reminder.reminderDate, 
                                                reminder.reminderTxt,
                                                reminder.reminderImg,
                                                reminder.reminderID,
                                                reminder.reminderType,
                                                reminder.status
                                            FROM reminder
                                            LEFT JOIN customer ON reminder.customerID = customer.customerID
                                            LEFT JOIN planner ON reminder.plannerID = planner.plannerID
                                            LEFT JOIN admin ON reminder.adminID = admin.adminID
                                            LEFT JOIN guest ON reminder.guestID = guest.guestID
                                            WHERE reminder.customerID = %s
                                            ORDER BY reminder.reminderID DESC;""", (customerID,))
        all_messages = self.__connection.fetchall()
        return all_messages
    

    def planner_view_messages(self, plannerID):
        self.__connection.execute ("""SELECT CONCAT(customer.firstName, ' ', customer.lastName) AS customerName,
                                                CONCAT(planner.firstName, ' ', planner.lastName) AS plannerName,
                                                CONCAT(admin.firstName, ' ', admin.lastName) AS adminName,
                                                CONCAT(guest.firstName, ' ',guest.lastName) AS guestName,
                                                reminder.reminderDate, 
                                                reminder.reminderTxt,
                                                reminder.reminderImg,
                                                reminder.reminderID,
                                                reminder.reminderType,
                                                reminder.status
                                            FROM reminder
                                            LEFT JOIN customer ON reminder.customerID = customer.customerID
                                            LEFT JOIN planner ON reminder.plannerID = planner.plannerID
                                            LEFT JOIN admin ON reminder.adminID = admin.adminID
                                            LEFT JOIN guest ON reminder.guestID = guest.guestID
                                            WHERE reminder.plannerID = %s
                                            ORDER BY reminder.reminderID DESC;""", (plannerID,))

        all_messages = self.__connection.fetchall()
        return all_messages
    
    
    def admin_view_messages(self, adminID):
        self.__connection.execute ("""SELECT CONCAT(customer.firstName, ' ', customer.lastName) AS customerName,
                                                CONCAT(planner.firstName, ' ', planner.lastName) AS plannerName,
                                                CONCAT(admin.firstName, ' ', admin.lastName) AS adminName,
                                                CONCAT(guest.firstName, ' ',guest.lastName) AS guestName,
                                                reminder.reminderDate, 
                                                reminder.reminderTxt,
                                                reminder.reminderImg,
                                                reminder.reminderID,
                                                reminder.reminderType,
                                                reminder.status
                                            FROM reminder
                                            LEFT JOIN customer ON reminder.customerID = customer.customerID
                                            LEFT JOIN planner ON reminder.plannerID = planner.plannerID
                                            LEFT JOIN admin ON reminder.adminID = admin.adminID
                                            LEFT JOIN guest ON reminder.guestID = guest.guestID
                                            WHERE reminder.adminID = %s
                                            ORDER BY reminder.reminderID DESC;""", (adminID,))
        all_messages = self.__connection.fetchall()
        return all_messages
    
    def mark_as_read(self, reminderID):
        # Mark a reminder as read by updating its status.
        self.__connection.execute("""UPDATE reminder SET status = 'read' WHERE reminderID = %s;""", (reminderID,))

    def unread_message_count_customer(self, customerID):
        # Get the count of unread messages for a specific customer.
        unread_count = self.__connection.execute("""SELECT COUNT(*) 
                                                            FROM reminder 
                                                            WHERE status = 'unread' AND customerID = %s;""", (customerID,))
        
        unread_count = self.__connection.fetchone()[0]
        return unread_count
    
    def unread_message_count_planner(self, plannerID):
        # Get the count of unread messages for a specific customer.
        unread_count = self.__connection.execute("""SELECT COUNT(*) 
                                                            FROM reminder 
                                                            WHERE status = 'unread' AND plannerID = %s;""", (plannerID,))
        
        unread_count = self.__connection.fetchone()[0]
        return unread_count
    
    def unread_message_count_admin(self, adminID):
        # Get the count of unread messages for a specific customer.
        unread_count = self.__connection.execute("""SELECT COUNT(*) 
                                                            FROM reminder 
                                                            WHERE status = 'unread' AND adminID = %s;""", (adminID,))
        
        unread_count = self.__connection.fetchone()[0]
        return unread_count

    def quote_message(self, today,customerID, message):
        self.__connection.execute("""INSERT INTO reminder (reminderDate, reminderType, customerID, reminderTxt) 
                                               VALUES (%s, 'Individual', %s, %s);""", 
                                               (today, customerID, message))
        
    def cancel_message(self, today,customerID, plannerID, message):
        self.__connection.execute("""INSERT INTO reminder (reminderDate, reminderType, customerID, plannerID, reminderTxt) 
                                               VALUES (%s, 'Individual', %s, %s, %s);""", 
                                               (today, customerID, plannerID, message))
        
    def delete_message(self, reminderID):
        self.__connection.execute("""DELETE FROM reminder WHERE reminderID = %s;""", (reminderID,))



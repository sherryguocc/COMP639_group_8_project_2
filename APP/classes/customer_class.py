from APP import getCursor

class Customer:

    @staticmethod
    def get_all_cust():
        connection = getCursor()
        connection.execute('SELECT * FROM customer')
        customer_list = connection.fetchall()
        return customer_list

    @staticmethod
    def get_cust_info(customerID):
        connection = getCursor()
        connection.execute("""SELECT * FROM customer WHERE customerID = %s;""", (customerID,))
        cust_user = connection.fetchone()
        return cust_user
    
    @staticmethod
    def customer_edit_profile(customerID, Title, FirstName, LastName, Phone, Email, Address, sql_dob):
        try:
            connection = getCursor()
            connection.execute("""UPDATE customer SET 
                        title = %s, firstName = %s, lastName = %s, phone = %s, email = %s, address = %s, DOB = %s WHERE customerID = %s;""",
                        (Title, FirstName, LastName, Phone, Email, Address, sql_dob, customerID))

        except Exception as e:
            print(f"Error while updating profile: {str(e)}")
            
    @staticmethod
    def customer_change_password(hashed_new_password, customerID):
        connection = getCursor()
        connection.execute("UPDATE customer SET PasswordHash = %s WHERE customerID = %s;", (hashed_new_password, customerID))

    @staticmethod
    def search_customer(search_query):
        connection = getCursor()
        connection.execute('SELECT * FROM customer WHERE firstName LIKE %s OR lastName LIKE %s OR email LIKE %s OR address LIKE %s;', 
                          ('%'+search_query+'%', '%'+search_query+'%', '%'+search_query+'%', '%'+search_query+'%'))
        return connection.fetchall()
    
    @staticmethod
    def get_customer_by_email(email):
        connection = getCursor()
        connection.execute("""SELECT email FROM customer WHERE email = %s;""", (email,))
        return connection.fetchone()
    
    @staticmethod
    def get_cust_by_bookingID(bookingID):
        connection = getCursor()
        connection.execute("SELECT customerID from booking WHERE bookingID = %s", (bookingID,))
        return connection.fetchone()[0]
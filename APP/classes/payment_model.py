from APP import getCursor

class Payment:
    def __init__(self, paymentID, bookingID, customerID, amount, bankAccount, paymentDate):
        self.__paymentID = paymentID
        self.__bookingID = bookingID
        self.__customerID = customerID
        self.__amount = amount
        self.__bankAccount = bankAccount
        self.__paymentDate = paymentDate

    @property
    def get_paymentID(self):
        return self.__paymentID
    
    @property
    def get_bookingID(self):
        return self.__bookingID

    @property
    def get_customerID(self):
        return self.__customerID

    @property
    def get_amount(self):
        return self.__amount

    @property
    def get_bankAccount(self):
        return self.__bankAccount

    @property
    def get_paymentDate(self):
        return self.__paymentDate


    def set_paymentID(self, paymentID):
        self.__paymentID = paymentID

    def set_bookingID(self, bookingID):
        self.__bookingID = bookingID

    def set_customerID(self, customerID):
        self.__customerID = customerID

    def set_amount(self, amount):
        self.__amount = amount

    def set_bankAccount(self, bankAccount):
        self.__bankAccount = bankAccount

    def set_paymentDate(self, paymentDate):
        self.__paymentDate = paymentDate

    @staticmethod
    def pay_booking (bookingID, customerID, amount, bankAccount, date):
        connection = getCursor()
        connection.execute("""INSERT INTO payment (bookingID, customerID, amount, bankAccount, paymentDate)
                VALUES (%s, %s, %s, %s, %s);
            """, (bookingID, customerID, amount, bankAccount, date))

    @staticmethod
    def refund_booking (bookingID, amount, date):
        connection = getCursor()
        connection.execute("""UPDATE payment SET amount = %s, paymentDate = %s WHERE bookingID = %s""", 
                           (amount, date, bookingID))
        
    @staticmethod
    def get_payment_by_booking_id(booking_id):
        connection = getCursor()
        connection.execute("""SELECT * FROM payment WHERE bookingID = %s;""", (booking_id,))
        payment_info = connection.fetchone()
        return payment_info
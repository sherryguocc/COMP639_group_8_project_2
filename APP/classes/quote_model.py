from APP import getCursor

class Quote:

    def __init__(self, 
                 bookingID, 
                 venue_fee, 
                 decor_fee, 
                 menu_price, 
                 additional_requirements, 
                 additional_fee,
                 discounts, 
                 notes, 
                 expiry_date, 
                 payment_terms, 
                 before_tax, 
                 gst_amount, 
                 total_include_gst,
                 quote_id = None, 
                 created_at = None):
        
        self.__quote_id = quote_id
        self.__bookingID = bookingID
        self.__venue_fee = venue_fee
        self.__decor_fee = decor_fee
        self.__menu_price = menu_price
        self.__additional_requirements = additional_requirements
        self.__additional_fee = additional_fee
        self.__discounts = discounts
        self.__notes = notes
        self.__expiry_date = expiry_date
        self.__payment_terms = payment_terms
        self.__before_tax = before_tax
        self.__gst_amount = gst_amount
        self.__total_include_gst = total_include_gst
        self.__created_at = created_at

    @property
    def quote_id(self):
        return self.__quote_id
    
    @property
    def bookingID(self):
        return self.__bookingID
    
    @property
    def venue_fee(self):
        return self.__venue_fee
    
    @property
    def decor_fee(self):
        return self.__decor_fee
    
    @property
    def menu_price(self):
        return self.__menu_price
    
    @ property 
    def additional_requirements (self):
        return self.__additional_requirements
    
    @property
    def additional_fee(self):
        return self.__additional_fee
    
    @property
    def discounts (self):
        return self.__discounts
    
    @property
    def notes (self):
        return self.__notes
    
    @property
    def expiry_date(self):
        return self.__expiry_date
    
    @property
    def payment_terms(self):
        return self.__payment_terms
    
    @property
    def before_tax (self):
        return self.__before_tax
    
    @property
    def gst_amount(self):
        return self.__gst_amount
    
    @property
    def total_amount(self):
        return self.__total_include_gst
    
    @property
    def created_at (self):
        return self.__created_at
    
    @quote_id.setter
    def quote_id(self, value):
        self.__quote_id = value

    @bookingID.setter
    def bookingID(self, value):
        self.__bookingID = value
    
    @venue_fee.setter
    def venue_fee(self, value):
        self.__venue_fee = value
    
    @decor_fee.setter
    def decor_fee(self, value):
        self.__decor_fee = value
    
    @menu_price.setter
    def menu_price(self, value):
        self.__menu_price = value
    
    @additional_requirements.setter
    def additional_requirements(self, value):
        self.__additional_requirements = value
    
    @additional_fee.setter
    def additional_fee(self, value):
        self.__additional_fee = value
    
    @discounts.setter
    def discounts(self, value):
        self.__discounts = value
    
    @notes.setter
    def notes(self, value):
        self.__notes = value
    
    @expiry_date.setter
    def expiry_date(self, value):
        self.__expiry_date = value
    
    @payment_terms.setter
    def payment_terms(self, value):
        self.__payment_terms = value
    
    @before_tax.setter
    def before_tax(self, value):
        self.__before_tax = value
    
    @gst_amount.setter
    def gst_amount(self, value):
        self.__gst_amount = value
    
    @total_amount.setter
    def total_amount(self, value):
        self.__total_include_gst = value
    
    @created_at.setter
    def created_at(self, value):
        self.__created_at = value

    # def new_quote (self):
    #     connection = getCursor()
    #     connection.execute("""INSERT INTO quotation (bookingID, venue_fee, decoration_fee, menu_price, 
    #                            additional_requirements, discounts, notes, expiry_date, 
    #                            payment_terms, total_before_tax, gst_amount, total_including_gst, 
    #                            created_at, additional_fee) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
    #                            (self.bookingID, self.venue_fee, self.decor_fee, self.menu_price,
    #                             self.additional_requirements, self.discounts, self.notes, 
    #                             self.expiry_date, self.payment_terms, self.before_tax, 
    #                             self.gst_amount, self.total_amount, self.created_at, self.additional_fee))

    def new_quote (self):
        connection = getCursor()
        connection.execute("""UPDATE quotation SET venue_fee = %s, decoration_fee = %s, menu_price = %s, 
                               additional_requirements = %s, discounts = %s, notes = %s, expiry_date = %s, 
                               payment_terms = %s, total_before_tax = %s, gst_amount = %s, total_including_gst = %s, 
                               created_at = %s, additional_fee = %s WHERE bookingID = %s""",
                               (self.venue_fee, self.decor_fee, self.menu_price,
                                self.additional_requirements, self.discounts, self.notes, 
                                self.expiry_date, self.payment_terms, self.before_tax, 
                                self.gst_amount, self.total_amount, self.created_at, self.additional_fee, self.bookingID))


    @staticmethod
    def get_quote (bookingID):
        connection = getCursor()
        connection.execute("""SELECT * FROM quotation WHERE bookingID =%s;""", (bookingID,))
        aQuote = connection.fetchone()
        return aQuote
    
    @staticmethod
    def get_quote_by_customerID(customerID):
        connection = getCursor()
        connection.execute("""SELECT * FROM quotation 
                                        JOIN booking ON quotation.bookingID = booking.bookingID
                                        WHERE customerID = %s""", (customerID,))
        quotes = connection.fetchall()
        return quotes



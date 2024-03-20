from APP import getCursor
import json

class Venue:
    def __init__(self,  venueID, venueName, eventArea, maxCapacity, location, status, dailyPrice, hourlyPrice, rented, description, image, type):
        # Constructor for the Venue class.
        self.__venueID = venueID
        self.__venueName = venueName
        self.__eventArea = eventArea
        self.__maxCapacity = maxCapacity
        self.__location = location
        self.__is_active = (status == 'Active') 
        self.__dailyPrice = dailyPrice
        self.__hourlyPrice = hourlyPrice
        self.__rented = bool(rented)
        self.__description = description
        self.__image = image
        self.__type = type
    
    # Property getters and setters for various attributes.
    # These allow controlled access to the private attributes.
    
    @property
    def get_venueID (self):
        return self.__venueID
    
    @property
    def get_venueName(self):
        return self.__venueName
    
    @get_venueName.setter
    def venueName(self, name):
        self.__venueName = name

    @property
    def get_eventArea(self):
        return self.__eventArea
    
    @get_eventArea.setter
    def eventArea(self, value):
        self.__eventArea = value

    @property
    def get_maxCapacity(self):
        return self.__maxCapacity
    
    @get_maxCapacity.setter
    def maxCapacity(self, value):
        self.__maxCapacity = value
    
    @property
    def get_status(self):
        return self.__is_active

    @property
    def get_location(self):
        return self.__location
    
    @get_location.setter
    def location(self, new_location):
        self.__location = new_location

    @property
    def is_active(self):
        return self.__is_active
    
    @is_active.setter
    def status (self, value):
        if not isinstance(value, bool):
            raise ValueError("is_active must be set to a boolean value")
        self.__is_active = value

    @property
    def get_dailyPrice(self):
        return self.__dailyPrice

    @get_dailyPrice.setter
    def dailyPrice(self, value):
        self.__dailyPrice = value

    @property
    def get_hourlyPrice(self):
        return self.__hourlyPrice

    @get_hourlyPrice.setter
    def hourlyPrice(self, value):
        self.__hourlyPrice = value
    
    @property
    def get_type(self):
        return self.__type

    @get_type.setter
    def type(self, value):
        self.__type = value

    @property
    def image_content(self):
        """
        Returns the image content. Parses if the image is stored in JSON format.
        
        Returns:
        - list: A list containing image data.
        """
        if isinstance(self.__image, list):  # If it's already a list, return it.
            return self.__image
        elif isinstance(self.__image, str):  # If it's a string, attempt to parse it as JSON.
            try:
                return json.loads(self.__image)
            except Exception as e:
                print(f"Error parsing image: {e}")
                return []
        else:  # If it's neither a list nor a string, return an empty list.
            return []
    
    @property
    def get_image(self):
        return self.__image
    
    @property
    def get_description(self):
        return self.__description
    
    @get_description.setter
    def description(self, description):
        self.__description = description
    
    @property
    def get_rented(self):
        return self.__rented
    
    @get_rented.setter
    def is_rented (self, value):
        if not isinstance(value, bool):
            raise ValueError("is_rented must be set to a boolean value")
        self.__is_rented = value
    
    @staticmethod
    def get_venue_list():
        """
        Retrieves a list of all venues from the database.

        Returns:
        - list: A list of Venue objects.
        """
        connection = getCursor()
        venueListQuery = """SELECT * FROM venue"""
        connection.execute(venueListQuery)
        rows = connection.fetchall()

        venue_list = []
        
        for row in rows:
            # Process each row and map columns to Venue attributes
            venue_id = row[0]
            venue_name = row[1]
            event_area = row[2]
            max_capacity = row[3]
            location = row[4]
            status = row[5] 
            daily_price = row[6]
            hourly_price = row[7]
            description = row[8]
            rented = True if row[9] == 1 else False
            image = row[10]
            type = row[11]
            
            # Create Venue object and append to the list
            venue = Venue(
                venueID=venue_id,
                venueName=venue_name,
                eventArea=event_area,
                maxCapacity=max_capacity,
                location=location,
                status=status,
                dailyPrice=daily_price,
                hourlyPrice=hourly_price,
                rented=rented,
                image=image,
                description=description,
                type=type
            )
            venue_list.append(venue)

        return venue_list
    
    @classmethod
    def get_venue_by_id(cls, venue_id):
        """
        Retrieves a specific venue based on its ID.

        Parameters:
        - venue_id (int): ID of the venue.

        Returns:
        - Venue: A Venue object or None if not found.
        """
        connection = getCursor()
        select_query = "SELECT * FROM venue WHERE venueID = %s"
        connection.execute(select_query, (venue_id,))
        row = connection.fetchone()

        if row:
            venue = cls(
                venueID=row[0],
                venueName=row[1],
                eventArea=row[2],
                maxCapacity=row[3],
                location=row[4],
                status=row[5],
                dailyPrice=row[6],
                hourlyPrice=row[7],
                image=row[10],
                description=row[8],
                rented=row[9],
                type=row[11]
            )
            return venue
        else:
            return None
    
    @classmethod
    def add_venue(cls, venue):
        try:
            connection = getCursor()
            insert_query = """INSERT INTO venue (venueName, eventArea, maxCapacity, location, status, dailyPrice, hourlyPrice, description, rented, image, type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            connection.execute(insert_query, (venue.get_venueName, venue.get_eventArea, venue.get_maxCapacity, venue.get_location, 'Active' if venue.is_active else 'Inactive', venue.get_dailyPrice, venue.get_hourlyPrice, venue.get_description, venue.get_rented, venue.get_image, venue.get_type))

        except Exception as e:
            print("Error while adding venue:", e)
            return False
    
    @classmethod
    def search(cls, search_query):
        """
        Searches for venues based on a given query (by name, event area, or location).

        Parameters:
        - search_query (str): Search keyword or phrase.

        Returns:
        - list: A list of Venue objects that match the search criteria.
        """
        venues = []
        connection = getCursor()
        search = """
            SELECT * FROM venue 
            WHERE venueName LIKE %s OR 
            (eventArea >= %s AND %s REGEXP '^-?[0-9]+$') OR 
            location LIKE %s
        """
        try:
            connection.execute(search, ('%' + search_query + '%', search_query, search_query, '%' + search_query + '%'))
            results = connection.fetchall()
            for row in results:
                venue = cls(
                    venueID=row[0],
                    venueName=row[1],
                    eventArea=row[2],
                    maxCapacity=row[3],
                    location=row[4],
                    status=row[5],
                    dailyPrice=row[6],
                    hourlyPrice=row[7],
                    rented=row[8],
                    description=row[9],
                    image=row[10],
                    type=row[11]
                )
                venues.append(venue)
        except Exception as ex:
            print(f"Query Error: {ex}")

        return venues
        
    @staticmethod
    def process_image_urls_to_list(image_urls_text):
        """
        Processes a text containing multiple image URLs, converting it to a list.

        Parameters:
        - image_urls_text (str): Text containing image URLs separated by newline.

        Returns:
        - list: A list containing individual image URLs.
        """
        # Split image URLs into a list
        image_urls_list = image_urls_text.strip().split('\n')
        return image_urls_list
    
    @staticmethod
    def process_image_urls_to_json(image_urls_text):
        """
        Processes a text containing multiple image URLs, converting it to a JSON formatted string.

        Parameters:
        - image_urls_text (str): Text containing image URLs separated by newline.

        Returns:
        - str: A JSON formatted string of image URLs.
        """

        # Split image URLs into a list
        image_urls_list = image_urls_text.strip().split('\n')       
        # Convert the list of image URLs to a JSON array
        image_urls_json = json.dumps(image_urls_list)
        return image_urls_json
    
    # Updates the current Venue object's details in the database.
    def update_to_database(self):
        connection = getCursor()
        select_query = "SELECT * FROM venue WHERE venueID = %s"
        connection.execute(select_query, (self.__venueID,))
        row = connection.fetchone()

        if row:
            attributes = {
                'venueName': self.get_venueName,
                'eventArea': self.get_eventArea,
                'maxCapacity': self.maxCapacity,
                'location': self.location,
                'status': 'Active' if self.is_active else 'Inactive',
                'dailyPrice': self.dailyPrice,
                'hourlyPrice': self.hourlyPrice,
                'description': self.description,
                'rented': self.__rented,
                'type': self.__type
            }

            for attr_name, attr_value in attributes.items():
                index = None
                if attr_name == 'venueName':
                    index = 1
                elif attr_name == 'eventArea':
                    index = 2
                elif attr_name == 'maxCapacity':
                    index = 3
                elif attr_name == 'location':
                    index = 4
                elif attr_name == 'status':
                    index = 5
                elif attr_name == 'dailyPrice':
                    index = 6
                elif attr_name == 'hourlyPrice':
                    index = 7
                elif attr_name == 'description':
                    index = 8
                elif attr_name == 'rented':
                    index = 9
                elif attr_name == 'type':
                    index = 10

                if index is not None and attr_value != row[index]:
                    update_query = f"UPDATE venue SET {attr_name} = %s WHERE venueID = %s"
                    connection.execute(update_query, (attr_value, self.__venueID))

        else:
            print('Venue not found in the database.')


    #Deletes the current Venue object from the database.
    def delete_venue(self):
        connection = getCursor()
        delete_query = "DELETE FROM venue WHERE venueID = %s"
        connection.execute(delete_query, (self.__venueID,))
    
    def delete_image(self, image_url_to_delete):
        """
        Removes a specific image URL from the current Venue object.

        Parameters:
        - image_url_to_delete (str): The image URL to be removed.
        """
        if isinstance(self.__image, list):
            image_list = self.__image
            image_list = [url.strip() for url in image_list]
        else:
            image_list = json.loads(self.__image) if self.__image else []

        image_url_to_delete_cleaned = image_url_to_delete.strip()
        
        if image_url_to_delete_cleaned in image_list:
            image_list.remove(image_url_to_delete_cleaned)
            connection = getCursor()
            update_query = """
            UPDATE venue
            SET image = %s
            WHERE venueID = %s
            """
            updated_image_json = json.dumps(image_list)
            connection.execute(update_query, (updated_image_json, self.__venueID))

    def add_image(self, image_urls_text):
        """
        Adds new image URLs to the current Venue object.

        Parameters:
        - image_urls_text (str): Text containing image URLs separated by newline.
        """
        new_image_list = self.process_image_urls_to_list(image_urls_text)
        connection = getCursor()
        # Create a placeholder for each image URL
        placeholders = ', '.join(['%s'] * len(new_image_list))
        # SQL query to append new URLs to the existing JSON array
        update_query = """
            UPDATE venue
            SET image = JSON_ARRAY_APPEND(COALESCE(image, '[]'), '$', """ + placeholders + """)
            WHERE venueID = %s
        """
        # Combine the new URLs and venueID as a tuple
        values = tuple(new_image_list) + (self.__venueID,)
        # Execute the query
        connection.execute(update_query, values)

    @classmethod
    def sort_venue_list(cls, venueList, sort_column, sort_direction):
        if sort_column == 'venueName':
            venueList.sort(key=lambda venue: venue.get_venueName, reverse=(sort_direction == 'desc'))
        elif sort_column == 'location':
            venueList.sort(key=lambda venue: venue.get_location, reverse=(sort_direction == 'desc'))
        elif sort_column == 'event_area':
            venueList.sort(key=lambda venue: venue.get_eventArea, reverse=(sort_direction == 'desc'))
        elif sort_column == 'capacity':
            venueList.sort(key=lambda venue: venue.get_maxCapacity, reverse=(sort_direction == 'desc'))
        elif sort_column == 'location':
            venueList.sort(key=lambda venue: venue.get_location, reverse=(sort_direction == 'desc'))
        elif sort_column == 'daily_price':
            venueList.sort(key=lambda venue: venue.get_dailyPrice, reverse=(sort_direction == 'desc'))
        elif sort_column == 'hourly_price':
            venueList.sort(key=lambda venue: venue.get_hourlyPrice, reverse=(sort_direction == 'desc'))
        elif sort_column == 'daily_price':
            venueList.sort(key=lambda venue: venue.get_dailyPrice, reverse=(sort_direction == 'desc'))
        elif sort_column == 'status':
            venueList.sort(key=lambda venue: venue.get_status, reverse=(sort_direction == 'desc'))
        return venueList
    
    def type_list(self):
            """
            Extracts type information from the type field and returns it as a list.
            """
            if self.__type:
                # Split the type field by commas and strip leading/trailing spaces
                type_list = [type.strip() for type in self.__type.split(',')]
                return type_list
            else:
                return []

    @classmethod
    def sort_venueList_by_type(cls, venueList, selected_type):
        # sorted the venue list by selected type
        if selected_type != 'all':
            filtered_venueList = [venue for venue in venueList if selected_type in venue.type_list()]
        else:
            filtered_venueList = venueList

        return filtered_venueList
    
    @classmethod
    def sort_venueList_by_status(cls, venueList, selected_status):
        # Filter the venue list by selected status
        if selected_status == 'Active':
            filtered_venueList = [venue for venue in venueList if venue.get_status]
        elif selected_status == 'Inactive':
            filtered_venueList = [venue for venue in venueList if not venue.get_status]
        else:
            # If selected_status is not 'active' or 'inactive', include all venues
            filtered_venueList = venueList

        return filtered_venueList
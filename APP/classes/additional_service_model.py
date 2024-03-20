from APP import getCursor

# Define the Decoration class for handling decorations.
class Decoration:
    # Constructor for the Decoration class.
    def __init__ (self, decorationID, decorationType, price, description):
        self.__ID = decorationID
        self.__type = decorationType
        self.__price = price
        self.__description = description

    # Property to get the decoration ID.
    @property
    def ID(self):
        return self.__ID

    # Property to get and set the decoration type.
    @property
    def decor_type (self):
        return self.__type

    @decor_type.setter
    def decor_type (self, new_decor):
        self.__type = new_decor

    # Property to get and set the decoration price.
    @property
    def price(self):
        return self.__price

    @price.setter
    def price(self, value):
        self.__price = value

    # Property to get and set the decoration description.
    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, value):
        self.__description = value

    # Class method to retrieve all decorations from the database.
    @classmethod
    def get_all_decorations(cls):
        connection = getCursor()
        connection.execute("SELECT * FROM decoration")
        return connection.fetchall()
    
    @staticmethod
    def get_decoration_list():
        """
        Retrieves a list of all decorations from the database.

        Returns:
        - list: A list of decoration objects.
        """
        connection = getCursor()
        decorationListQuery = """SELECT * FROM decoration"""
        connection.execute(decorationListQuery)
        rows = connection.fetchall()

        decoration_list = []
        
        for row in rows:
            # Process each row and map columns to decoration attributes
            decorationID = row[0]
            decorationType= row[1]
            price = row[2]
            description = row[3]
            
            # Create decoration object and append to the list
            decoration = Decoration(
                decorationID=decorationID,
                decorationType=decorationType,
                price=price,
                description=description,
            )
            decoration_list.append(decoration)

        return decoration_list
    
    @classmethod
    def sort_decoration_list(cls, decorationList, sort_column, sort_direction):
        if sort_column == 'type':
            decorationList.sort(key=lambda decoration: decoration.decor_type, reverse=(sort_direction == 'desc'))
        elif sort_column == 'price':
            decorationList.sort(key=lambda decoration: decoration.price, reverse=(sort_direction == 'desc'))
        elif sort_column == 'description':
            decorationList.sort(key=lambda decoration: decoration.description, reverse=(sort_direction == 'desc'))
        return decorationList
    
    @classmethod
    def add_decoration(cls, decoration):
        try:
            connection = getCursor()
            insert_query = """INSERT INTO decoration (decorationType, price, description)
            VALUES (%s, %s, %s)"""
            connection.execute(insert_query, (decoration.decor_type, decoration.price, decoration.description))
        except Exception as e:
            print("Error while adding decoration:", e)
            return False
        
    @classmethod
    def get_decoration_by_id(cls, decoration_id):
        """
        Retrieves a specific decoration based on its ID.

        Parameters:
        - decoration_id (int): ID of the decoration.

        Returns:
        - decoration: A decoration object or None if not found.
        """
        connection = getCursor()
        select_query = "SELECT * FROM decoration WHERE decorationID = %s"
        connection.execute(select_query, (decoration_id,))
        row = connection.fetchone()

        if row:
            decoration = cls(
                decorationID=row[0],
                decorationType=row[1],
                price=row[2],
                description=row[3]
            )
            return decoration
        else:
            return None
    
    @classmethod
    def get_decoration_by_type(cls, decoration_type):
        """
        Retrieves a specific decoration based on its type.

        Parameters:
        - decoration_type (str): type of the decoration.

        Returns:
        - decoration: A decoration object or None if not found.
        """
        connection = getCursor()
        select_query = "SELECT * FROM decoration WHERE decorationType = %s"
        connection.execute(select_query, (decoration_type,))
        row = connection.fetchone()

        if row:
            decoration = cls(
                decorationID=row[0],
                decorationType=row[1],
                price=row[2],
                description=row[3]
            )
            return decoration
        else:
            return None
        
    # Updates the current decoration object's details in the database.
    def update_to_database(self):
        connection = getCursor()
        select_query = "SELECT * FROM decoration WHERE decorationID = %s"
        connection.execute(select_query, (self.__ID,))
        row = connection.fetchone()

        if row:
            attributes = {
                'decorationType': self.decor_type,
                'price': self.price,
                'description': self.description,
            }

            for attr_type, attr_value in attributes.items():
                index = None
                if attr_type == 'decorationType':
                    index = 1
                elif attr_type == 'price':
                    index = 2
                elif attr_type == 'description':
                    index = 3
    
                if index is not None and attr_value != row[index]:
                    update_query = f"UPDATE decoration SET {attr_type} = %s WHERE decorationID = %s"
                    connection.execute(update_query, (attr_value, self.__ID))

        else:
            print('decoration not found in the database.')

    #Deletes the current decoration object from the database.
    def delete_decoration(self):
        connection = getCursor()
        delete_query = "DELETE FROM decoration WHERE decorationID = %s"
        connection.execute(delete_query, (self.__ID,))

# Define the Menu class for handling food menu items.
class Menu:
    # Constructor for the Menu class.
    def __init__(self, food_id, name, price, image, description):
        self.__ID = food_id
        self.__name = name
        self.__price = price
        self.__image = image
        self.__description = description

    # Property to get the food item ID.
    @property
    def food_id(self):
        return self.__ID
    
    # Property to get the food item name.
    @property
    def name(self):
        return self.__name

    # Property to set the food item name.
    @name.setter
    def name(self, value):
        self.__name = value

    # Property to get the food item price.
    @property
    def price(self):
        return self.__price

    # Property to set the food item price.
    @price.setter
    def price(self, value):
        if 0 <= value <= 20000:
            self._price = value
        else:
            raise ValueError("Price must be between 0 and 20000.")

    # Property to get the food item image.
    @property
    def image(self):
        return self.__image

    # Property to set the food item image
    @image.setter
    def image(self, value):
        self.__image = value

    @property
    def description(self):
        return self.__description

    # Property to set the food item description.
    @description.setter
    def description(self, value):
        self.__description = value


    # Class method to retrieve all menu items from the database.
    @classmethod
    def get_all_menus(cls):
        connection = getCursor()
        connection.execute("SELECT * FROM menu")
        return connection.fetchall()
    
    # Class method to get the image URL for a specific food item by its ID.
    @classmethod
    def get_image_by_food_id(cls, food_id):
        connection = getCursor()
        connection.execute("SELECT image FROM menu WHERE foodID = %s;", (food_id,))
        result = connection.fetchone()
        return result[0][0] if result else None
    
    @staticmethod
    def get_menu_list():
        """
        Retrieves a list of all menus from the database.

        Returns:
        - list: A list of menu objects.
        """
        connection = getCursor()
        menuListQuery = """SELECT * FROM menu"""
        connection.execute(menuListQuery)
        rows = connection.fetchall()

        menu_list = []
        
        for row in rows:
            # Process each row and map columns to menu attributes
            food_id = row[0]
            name = row[1]
            price = row[2]
            image = row[3]
            description = row[4]
            
            # Create menu object and append to the list
            menu = Menu(
                food_id=food_id,
                name=name,
                price=price,
                image=image,
                description=description,
            )
            menu_list.append(menu)

        return menu_list
    
    @classmethod
    def sort_menu_list(cls, menuList, sort_column, sort_direction):
        if sort_column == 'name':
            menuList.sort(key=lambda menu: menu.name, reverse=(sort_direction == 'desc'))
        elif sort_column == 'price':
            menuList.sort(key=lambda menu: menu.price, reverse=(sort_direction == 'desc'))
        elif sort_column == 'description':
            menuList.sort(key=lambda menu: menu.description, reverse=(sort_direction == 'desc'))
        return menuList
    
    @classmethod
    def add_menu(cls, menu):
        try:
            connection = getCursor()
            insert_query = """INSERT INTO menu (name, price, image, description)
            VALUES (%s, %s, %s, %s)"""
            connection.execute(insert_query, (menu.name, menu.price, "/"+ menu.image, menu.description))
        except Exception as e:
            print("Error while adding menu:", e)
            return False
        
    @classmethod
    def get_menu_by_id(cls, menu_id):
        """
        Retrieves a specific menu based on its ID.

        Parameters:
        - menu_id (int): ID of the menu.

        Returns:
        - menu: A menu object or None if not found.
        """
        connection = getCursor()
        select_query = "SELECT * FROM menu WHERE foodID = %s"
        connection.execute(select_query, (menu_id,))
        row = connection.fetchone()

        if row:
            menu = cls(
                food_id=row[0],
                name=row[1],
                price=row[2],
                image=row[3],
                description=row[4]
            )
            return menu
        else:
            return None
    
    @classmethod
    def get_menu_by_name(cls, menu_name):
        """
        Retrieves a specific menu based on its name.

        Parameters:
        - menu_name (str): Name of the menu.

        Returns:
        - menu: A menu object or None if not found.
        """
        connection = getCursor()
        select_query = "SELECT * FROM menu WHERE name = %s"
        connection.execute(select_query, (menu_name,))
        row = connection.fetchone()

        if row:
            menu = cls(
                food_id=row[0],
                name=row[1],
                price=row[2],
                image=row[3],
                description=row[4]
            )
            return menu
        else:
            return None
        
    @classmethod
    def delete_image(cls, menu_id):
        """
        Removes the image of a specific menu item.

        Parameters:
        - menu_id (int): The ID EREof the menu item to remove the image from.
        """
        menu = Menu.get_menu_by_id(menu_id)
        if menu:
            connection = getCursor()
            delete_query = """
                UPDATE menu
                SET image = NULL
                WHERE foodID = %s
            """
            connection.execute(delete_query, (menu_id,))
    
    # Updates the current menu object's details in the database.
    def update_to_database(self):
        connection = getCursor()
        select_query = "SELECT * FROM menu WHERE foodID = %s"
        connection.execute(select_query, (self.__ID,))
        row = connection.fetchone()

        if row:
            attributes = {
                'name': self.name,
                'price': self.price,
                'description': self.description,
                'image':self.image
            }

            for attr_name, attr_value in attributes.items():
                index = None
                if attr_name == 'name':
                    index = 1
                elif attr_name == 'price':
                    index = 2
                elif attr_name == 'image':
                    index = 3 
                elif attr_name == 'description':
                    index = 4
                
                if index is not None and attr_value != row[index]:
                    update_query = f"UPDATE menu SET {attr_name} = %s WHERE foodID = %s"
                    connection.execute(update_query, (attr_value, self.__ID))

        else:
            print('menu not found in the database.')

    #Deletes the current menu object from the database.
    def delete_menu(self):
        connection = getCursor()
        delete_query = "DELETE FROM menu WHERE foodID = %s"
        connection.execute(delete_query, (self.__ID,))

    @image.setter
    def image(self, new_image):
        # Update the database with the new image
        connection = getCursor()
        update_query = "UPDATE menu SET image = %s WHERE foodID = %s"
        connection.execute(update_query, (new_image, self.__ID))
    
    @classmethod
    def update_image(cls, image, menu_id):
        """
        Update the image of a specific menu item.

        Parameters:
        - menu_id (int): The ID EREof the menu item to remove the image from.
        """
        menu = Menu.get_menu_by_id(menu_id)
        if menu:
            connection = getCursor()
            update_query = """
                UPDATE menu
                SET image = %s
                WHERE foodID = %s
            """
            connection.execute(update_query, (image, menu_id,))
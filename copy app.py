import mysql.connector

pwd = open("pass.txt","r").read().strip()
connector = mysql.connector.connect(
    host = "127.0.0.1",
    user="root",
    password = pwd
)

cursor = connector.cursor()
cursor.execute("use alldeez;")

def init_screen():
    print("Welcome to alldeez")
    print("1. Login as user")
    print("2. Register as user")
    print("3. Login as seller")
    print("4. Register as seller")
    print("5. Login as admin")
    print("6. Login as delivery person")
    print("7. Register as delivery person")
    print("8. Exit")
    choice = input("Please enter your choice: ")
    if choice == "1":
        user_login()
    elif choice == "2":
        user_register()
    elif choice == "3":
        seller_login()
    elif choice == "4":
        seller_register()
    elif choice == "5":
        admin_login()
    elif choice == "6":
        delivery_person_login()
    elif choice == "7":
        delivery_person_register()
    elif choice == "8":
        exit()

def user_login():
    count = 0
    print("Welcome to alldeez. Please use your credentials to login")
    username = input("Username: ")
    password = input("Password: ")
    cursor.execute("SELECT * FROM users WHERE username = %s AND pass = %s", (username, password))
    if cursor.fetchone():
        print("Login successful")
        user_mainmenu(username)
    else:
        print("Login failed, try again")
        count += 1
        if(count>=5):
            print("Too many attempts, please reset your password.")
            forgot_password(username)
        user_login()

def forgot_password(username):
    cursor.execute("SELECT * FROM users WHERE Username = %s", (username,))
    result = cursor.fetchone()
    print("Please enter your new password:")
    new_password = input()
    cursor.execute("UPDATE users SET pass = %s WHERE Username = %s", (new_password, username))
    connector.commit()
    print("Password updated successfully!")
    
def user_mainmenu(user):
    print("Welcome to alldeez, " + user)
    print("1. View your orders")
    print("2. View your account details")
    print("3. View pending returns")
    print("4. View product categories")
    print("5. View your cart and Place an order")
    print("6. Add a product")
    print("7. Logout")
    choice = input("Please enter your choice: ")
    if choice == "1":
        view_orders(user)
    elif choice == "2":
        view_account(user)
    elif choice == "3":
        view_returns(user)
    elif choice == "4":
        view_categories()
    elif choice == "5":
        view_cart(user)
    elif choice == "6":
        add_to_cart(user)
    elif choice == "7":
        init_screen()
    else:
        print("Invalid choice. Please try again.")
        user_mainmenu(user)

def user_register():
    print("Welcome to alldeez. Please use your credentials to register")
    username = input("Username: ")
    password = input("Password: ")
    email = input("Email: ")
    fullname = input("Fullname: ")
    useraddress = input("Address: ")
    phonenumber = input("Phone number: ")
    cursor.execute("INSERT INTO users (username, pass, email, fullname, useraddress, phonenumber) VALUES (%s, %s, %s, %s, %s, %s)", (username, password, email, fullname, useraddress, phonenumber))
    connector.commit()
    print("Registration successful")
    user_login()

def view_orders(user):
    cursor.execute("SELECT * FROM orders JOIN users on users.userid = orders.userid WHERE users.username = %s", (user,))
    orders = cursor.fetchall()
    for order in orders:
        print(order)
    user_mainmenu(user)
    
def view_account(user):
    cursor.execute("SELECT username, email, fullname, useraddress, phonenumber FROM users WHERE username = %s", (user,))
    username, email, fullname, useraddress, phonenumber = cursor.fetchone()
    print(f"Username: {username}")    
    print(f"Email: {email}")    
    print(f"Fullname: {fullname}")
    print(f"Address: {useraddress}")
    print(f"Phone: {phonenumber}")
    user_mainmenu(user)

def view_returns(user):
    query = "SELECT * FROM returns WHERE user=%s"
    values = (user,)
    cursor.execute(query, values)
    returns = cursor.fetchall()

    if not returns:
        print("You have no returns to view.")
        return

    # display the returns to the user
    print("Your returns:")
    for r in returns:
        print(f"Return ID: {r[0]}\nProduct ID: {r[1]}\nReason: {r[2]}\nStatus: {r[3]}\n")

def view_categories():
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    print("Available Categories:")
    for category in categories:
        print(f"{category[0]}. {category[1]}")
    choice = input("Enter category ID to view products: ")
    try:
        category_id = int(choice)
        view_category_products(category_id)
    except ValueError:
        print("Invalid input. Please enter a number.")
        view_categories()

def view_category_products(category_id):
    cursor.execute("SELECT * FROM products WHERE categoryid = %s", (category_id,))
    products = cursor.fetchall()
    if products:
        print(f"Products under category {category_id}:")
        for product in products:
            print(f"Product ID: {product[0]}, Name: {product[3]}, Price: {product[4]}")
    else:
        print("No products found under this category.")   

def view_cart(user):
    # Retrieve all products in user's cart
    query = "SELECT products.id, products.name, products.price, cart.quantity FROM cart JOIN products ON cart.product_id = products.id WHERE cart.user_id=%s"
    cursor.execute(query, (user,))
    cart_items = cursor.fetchall()

    # Display cart items
    if not cart_items:
        print("Your cart is empty.")
        return

    print("Your cart:")
    total_price = 0
    for item in cart_items:
        item_price = item[2] * item[3]
        total_price += item_price
        print(f"ID: {item[0]}, Name: {item[1]}, Price: {item[2]}, Quantity: {item[3]}, Item Total: {item_price}")

    print(f"Total price: {total_price}")

    # Prompt user to place order
    confirm = input("Do you want to place an order? (y/n): ")

    if confirm.lower() == "y":
        # Clear user's cart
        query = "DELETE FROM cart WHERE user_id=%s"
        cursor.execute(query, (user,))
        connector.commit()

        # Insert order into orders table
        query = "INSERT INTO orders (userid, haspaid) VALUES (%s, %s)"
        values = (user, 1)
        cursor.execute(query, values)
        connector.commit()

        print("Order placed successfully!")
    else:
        pass

def add_to_cart(user):
    # Display list of existing products
    query = "SELECT productid, productname, Price, productdesc, quantity FROM products"
    cursor.execute(query)
    products = cursor.fetchall()

    print("Available products:")
    for p in products:
        print(f"ID: {p[0]}, Name: {p[1]}, Price: {p[2]}, Quantity: {p[4]}")

    # Prompt user to select a product
    product_id = int(input("Enter the ID of the product you want to add to your cart: "))
    quantity = int(input("Enter the quantity you want to add: "))

    # Check if product is available and has enough quantity
    query = "SELECT productid, quantity FROM products WHERE productid=%s"
    cursor.execute(query, (product_id,))
    product = cursor.fetchone()

    if not product:
        print("Product not found.")
        return

    if product[1] < quantity:
        print("Not enough quantity available.")
        return

    # Insert product into cart
    query = "INSERT INTO carts (userid, productid, quantity) VALUES (%s, %s, %s)"
    values = (user, product_id, quantity)
    cursor.execute(query, values)
    connector.commit()

    print("Product successfully added to cart!")

def seller_login():
    print("Welcome to alldeez. Please use your credentials to login")
    username = input("Username: ")
    password = input("Password: ")
    cursor.execute("SELECT * FROM sellers WHERE username = %s AND pass = %s", (username, password))
    if cursor.fetchone():
        print("Login successful")
        seller_mainmenu(username)
    else:
        print("Login failed, try again")
        seller_login()

def seller_register():
    print("Welcome to alldeez. Please use your credentials to register")
    username = input("Username: ")
    password = input("Password: ")
    name = input("Name: ")
    number = input("Number: ")
    cursor.execute("INSERT INTO sellers (username, pass, sellername, phonenumber) VALUES (%s, %s, %s, %s)", (username, password, name, number))
    connector.commit()
    print("Registration successful")
    seller_login()

def seller_mainmenu(seller):
    print("Welcome to alldeez, " + seller)
    print("1. View your products")
    print("2. View your account details")
    print("3. View your sales")
    print("4. Add a new product")
    print("5. Delete a product")
    print("6. Logout")

    choice = input("Please enter your choice: ")
    if choice == "1":
        view_products(seller)
    elif choice == "2":
        view_selleraccount(seller)
    elif choice == "3":
        view_sales(seller)
    elif choice == "4":
        add_product(seller)
    elif choice == "5":
        delete_product(seller)
    elif choice == "6":
        init_screen()
    else:
        print("Invalid choice. Please try again.")
        seller_mainmenu(seller)

def view_products(seller):
    cursor.execute("SELECT * FROM products JOIN sellers on sellers.sellerid = products.sellerid WHERE sellers.username = %s", (seller,))
    products = cursor.fetchall()
    for product in products:
        print(product)
    seller_mainmenu(seller)

def view_selleraccount(seller):
    cursor.execute("SELECT username, sellername, phonenumber FROM sellers WHERE username = %s", (seller,))
    username, sellername, phonenumber = cursor.fetchone()
    print(f"Username: {username}")    
    print(f"Sellername: {sellername}")
    print(f"Phone: {phonenumber}")
    seller_mainmenu(seller)

def view_sales(seller):
    # get the products that belong to the seller
    query = "SELECT productid, productname, price FROM products WHERE sellerid=%s"
    cursor.execute(query, (seller,))
    products = cursor.fetchall()
    
    total_revenue = 0
    
    # for each product, get the quantity sold and print it
    for product in products:
        product_id, product_name, price = product
        query = """
            SELECT SUM(quantity) FROM orders 
            JOIN products ON orders.productid = products.productid
            WHERE products.sellerid = %s AND orders.haspaid = 1 AND orders.delivererid IS NOT NULL
            AND orders.productid = %s
        """
        cursor.execute(query, (seller, product_id))
        quantity_sold = cursor.fetchone()[0]
        if quantity_sold is None:
            quantity_sold = 0
        total_price = quantity_sold * price
        total_revenue += total_price
        print(f"{product_name}: {quantity_sold} (total price: {total_price})")
    
    print(f"Total revenue for {seller}: {total_revenue}")


def add_product(seller):
    print("Please enter the details of the product")
    name = input("Name: ")
    price = input("Price: ")
    category = input("Category: ")
    cursor.execute("SELECT categoryid FROM categories WHERE categoryname = %s", (category,))
    categoryid = cursor.fetchone()[0]
    cursor.execute("SELECT sellerid FROM sellers WHERE username = %s", (seller,))
    sellerid = cursor.fetchone()[0]
    desc = input("Description: ")
    cursor.execute("INSERT INTO products (productname, price, categoryid, sellerid, productdesc) VALUES (%s, %s, %s, %s, %s)", (name, price, categoryid, sellerid, desc))
    connector.commit()
    print("Product added")
    seller_mainmenu(seller)

def delete_product(seller):
    product_id = input("Please enter the ID of the product you want to delete: ")
    confirm = input("Are you sure you want to delete this product? (y/n): ")
    if confirm.lower() == "y":
        # delete the product from the database
        query = "DELETE FROM products WHERE seller=%s AND id=%s"
        values = (seller, product_id)
        cursor.execute(query, values)
        connector.commit()
        print("Product successfully deleted!")
    else:
        print("Product deletion cancelled.")

def admin_login():
    print("Welcome to alldeez. Please use your credentials to login")
    admin_user = "sid"
    admin_pass = "123"
    username = input("Username: ")
    password = input("Password: ")
    if username == admin_user and password == admin_pass:
        print("Login successful")
        admin_screen()
    else:
        print("Login failed, try again")
        admin_login()

def admin_screen():
    print("Admin screen:")
    print("1. Ban a user")
    print("2. Ban a seller")
    print("3. Ban a delivery person")
    print("4. Get details of a user")
    print("5. Get details of a seller")
    print("6. Get details of a delivery person")
    print("7. Get details of orders")
    print("8. Logout")
    choice = input("Please enter your choice: ")
    if choice == "1":
        ban_user()
    elif choice == "2":
        ban_seller()
    elif choice == "3":
        ban_deliveryperson()
    elif choice == "4":
        seller = input("Username: ")
        view_seller(seller)
    elif choice == "5":
        user = input("Username: ")
        view_user(user)
    elif choice == "6":
        delivery_person = input("Username: ")
        view_delivery_person(delivery_person)
    elif choice == "7":
        view_orders()
    elif choice == "8":
        init_screen()
    else:
        admin_screen()

def ban_user():
    username = input("Enter the username of the user to be banned: ")
    cursor.execute("DELETE FROM users WHERE username = %s", (username,))
    connector.commit()
    print("User banned")
    admin_screen()

def ban_seller():
    username = input("Enter the username of the seller to be banned: ")
    cursor.execute("DELETE FROM sellers WHERE username = %s", (username,))
    connector.commit()
    print("Seller banned")
    admin_screen()

def ban_deliveryperson():
    delivery_id = input("Enter the ID of the delivery person to be banned: ")
    cursor.execute("SELECT * FROM delivery_persons WHERE deliveryid=%s", (delivery_id,))

    result = cursor.fetchone()
    if result:
        cursor.execute("DELETE FROM delivery_persons WHERE deliveryid=%s", (delivery_id,))
        print("Delivery person banned successfully!")
    else:
        print("No delivery person found with that ID")
    admin_screen()

def view_seller(seller):
    cursor.execute(f"SELECT * FROM sellers WHERE sellername='{seller}'")
    myresult = cursor.fetchone()
    if myresult:
        print("Seller ID:", myresult[0])
        print("Username:", myresult[1])
        print("Password:", myresult[2])
        print("Seller Name:", myresult[3])
        print("Phone Number:", myresult[4])
    else:
        print("No seller found with the given name.")

def view_user(user):
    cursor.execute(f"SELECT * FROM users WHERE Username='{user}'")
    myresult = cursor.fetchone()
    if myresult:
        print("User ID:", myresult[0])
        print("Username:", myresult[1])
        print("Email:", myresult[2])
        print("Password:", myresult[3])
        print("Full Name:", myresult[4])
        print("Address:", myresult[5])
        print("Phone Number:", myresult[6])
    else:
        print("No user found with the given name.")

def view_delivery_person(delivery_person):
    cursor.execute("SELECT * FROM delivery_persons WHERE deliveryname=%s", (delivery_person,))

    # Fetch the result of the query and print the information
    result = cursor.fetchone()
    if result:
        print("Delivery person ID: ", result[0])
        print("Delivery person name: ", result[1])
        print("Delivery person phone number: ", result[2])
    else:
        print("No delivery person found with that name")

def view_orders():
    cursor.execute("SELECT * FROM orders")

    # iterate over the result set and print each row
    for order in cursor.fetchall():
        print(f"Order ID: {order[0]}")
        print(f"User ID: {order[1]}")
        print(f"Has Paid: {order[2]}")
        print(f"Deliverer ID: {order[3]}")
        print()

def delivery_person_login():
    pass
def delivery_person_register():
    pass
def update_status(order):
    pass
def view_deliveries(deliveryid):
    pass


init_screen()

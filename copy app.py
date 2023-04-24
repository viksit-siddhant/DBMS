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
    print("4. Browse products")
    print("5. View your cart and Place an order")
    print("6. Add a product")
    print("7. Review a product")
    print("8. Request a return")
    print("9. Empty a cart")
    print("10. Logout")
    choice = input("Please enter your choice: ")
    if choice == "1":
        view_orders(user)
    elif choice == "2":
        view_account(user)
    elif choice == "3":
        view_returns(user)
    elif choice == "4":
        browse_products()
    elif choice == "5":
        view_cart(user)
    elif choice == "6":
        add_to_cart(user)
    elif choice == "7":
        review_product(user)
    elif choice == "8":
        add_return(user)
    elif choice == "9":
        cursor.execute("SELECT orderid FROM orders WHERE userid = (SELECT userid FROM users WHERE username = %s) ORDER BY orderid DESC", (user,))
        orderid = cursor.fetchone()[0]
        cursor.fetchall()
        cursor.execute("DELETE FROM orders WHERE orderid = %s", (orderid,))
    elif choice =="10":
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
    query = "SELECT * FROM prod_returns WHERE userid=%s"
    values = (user,)
    cursor.execute(query, values)
    returns = cursor.fetchall()

    if not returns:
        print("You have no returns to view.")
        return

    # display the returns to the user
    print("Your returns:")
    for r in returns:
        print(f"Return ID: {r[0]}\nProduct ID: {r[1]}\nUser ID: {r[2]}\nStatus: {r[3]}\n")

def browse_products(user):
    cursor.execute("SELECT productid, productname, price, sellername FROM products JOIN sellers ON sellers.sellerid = products.sellerid")
    print(" \t\tName\t\tPrice\t\tSeller")
    for i,row in enumerate(cursor.fetchall()):
        print(row[0],"\t\t",row[1],"\t\t",row[2],"\t\t",row[3])
    print("1. Add to cart")
    print("2. Go back")
    choice = input("Please enter your choice: ")
    if choice == "1":
        id = input("Enter product id: ")
        quantity = input("Enter quantity: ")
        cursor.execute("SELECT orderid FROM orders WHERE userid = (SELECT userid FROM users WHERE username = %s) ORDER BY orderid DESC", (user,))
        orderid = cursor.fetchone()[0]
        cursor.fetchall()
        cursor.execute("INSERT INTO carts (orderid, productid, quantity) VALUES (%s, %s, %s)", (orderid, id, quantity))
        cursor.fetchall()
        connector.commit()
        browse_products(user)
        
    elif choice == "2":
        user_mainmenu(user)

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
        place_order(user, total_price)
    else:
        pass

def place_order(user, total_price):
    # Prompt user to select payment method
    print("Select payment method:")
    print("1. Credit Card")
    print("2. Debit Card")
    print("3. Net Banking")
    print("4. Cash")
    choice = int(input("Enter your choice: "))

    # Process payment
    if choice == 1:
        # Process credit card payment
        card_number = input("Enter your card number: ")
        card_expiry = input("Enter your card expiry date (MM/YY): ")
        card_cvv = input("Enter your card CVV: ")
        print("Credit card payment processed successfully.")
        has_paid = 1
    elif choice == 2:
        # Process debit card payment
        card_number = input("Enter your card number: ")
        card_expiry = input("Enter your card expiry date (MM/YY): ")
        card_cvv = input("Enter your card CVV: ")
        print("Debit card payment processed successfully.")
        has_paid = 1
    elif choice == 3:
        # Process net banking payment
        print("Net banking payment processed successfully.")
        has_paid = 1
    else:
        print("Your payment status has been updated to cash on delivery.")
        has_paid = 0

    # Clear user's cart
    query = "DELETE FROM cart WHERE user_id=%s"
    cursor.execute(query, (user,))
    connector.commit()

    # Insert order into orders table
    query = "INSERT INTO orders (userid, totalprice, haspaid) VALUES (%s, %s, %s)"
    values = (user, total_price, has_paid)
    cursor.execute(query, values)
    connector.commit()

    print("Order placed successfully and will be delivered within next 5-6 working days!")
    
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

def review_product(user):
    # Prompt user to enter product ID
    product_id = input("Enter product ID to review: ")

    # Check if product exists in the database
    cur.execute("SELECT productname FROM products WHERE productid=%s", (product_id,))
    product = cur.fetchone()
    if product is None:
        print("Product not found. Please try again.")
        review_product(user)
        return

    # Prompt user to enter rating for the product
    rating = input("Enter rating (1-5): ")

    # Check if rating is valid
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            raise ValueError
    except ValueError:
        print("Invalid rating. Please enter a number between 1 and 5.")
        review_product(user)
        return

    # Insert review into the database
    cur.execute("INSERT INTO reviews (productid, userid, Rating) VALUES (%s, %s, %s)", (product_id, user_id, rating))
    conn.commit()

    print("Review added successfully.")

def add_return(user):
    print("This is the return policy of our retail store.")
    print()
    print("We have a 30-day return policy for all products purchased from our store.")
    print("If you are not satisfied with your purchase, you may return it within 30 days of the delivery date.")
    print("To initiate a return, please log in to your account and go to the 'Request a Return' option in the user menu.")
    print("You will be asked to provide the reason for the return and to select a return method.")
    print("Once your return request is approved, you will receive further instructions on how to proceed.")
    print()
    order_id = input("Enter the order ID for the product you want to return: ")
    reason = input("Enter the reason for the return: ")
    product_id = input("Enter the product ID for the product you want to return: ")

    # insert return request into prod_returns table
    cursor.execute("INSERT INTO prod_returns (orderid, userid, reason, productid, status) VALUES (%s, %s, %s, %s, %s)", (order_id, get_user_id(user), reason, product_id, "Pending"))
    connector.commit()
    print("Return request submitted successfully.")
    user_mainmenu(user)
    
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
    print("4. See geographical sales data")
    print("5. Add a new product")
    print("6. Delete a product")
    print("7. Logout")

    choice = input("Please enter your choice: ")
    if choice == "1":
        view_products(seller)
    elif choice == "2":
        view_selleraccount(seller)
    elif choice == "3":
        view_sales(seller)
    elif choice == "4":
        cursor.execute("SELECT ordercity,orderstate, SUM(p.price) FROM orders JOIN cart ON orders.orderid = cart.orderid JOIN products p ON cart.productid = p.productid JOIN sellers s ON p.sellerid = s.sellerid WHERE s.username = %s GROUP BY ordercity, orderstate WITH ROLLUP", (seller,))
        for row in cursor.fetchall():
            print(row)
    elif choice == "5":
        add_product(seller)
    elif choice == "6":
        delete_product(seller)
    elif choice == "7":
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
    print("8. List all users")
    print("9. Logout")
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
        view_all_users()
    elif choice == "9":
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

def view_all_users():
    query = "SELECT * FROM users"
    cursor.execute(query)
    users = cursor.fetchall()

    if not users:
        print("There are no users in the database.")
        return

    # display the users to the console
    print("Users:")
    for user in users:
        print(f"User ID: {user[0]}\nUsername: {user[1]}\nEmail: {user[2]}\nFull Name: {user[4]}\nAddress: {user[5]}\nPhone Number: {user[6]}\n")

        
def delivery_person_login():
    max_attempts = 5
    num_attempts = 0
    
    while num_attempts < max_attempts:
        # get delivery person's phone number and check if it exists in the database
        phone_num = input("Enter delivery person's phone number: ")
        query = "SELECT * FROM delivery_persons WHERE Phonenumber=%s"
        values = (phone_num,)
        cursor.execute(query, values)
        delivery_person = cursor.fetchone()

        if delivery_person:
            print(f"Welcome, {delivery_person[1]}!")
            delivery_person_screen(phone_num)
        else:
            print("Invalid phone number. Please try again.")
            num_attempts += 1

    # maximum number of login attempts reached
    print("Maximum login attempts reached. Please try again later.")
    
def delivery_person_register():
    deliveryname = input("Enter delivery person's name: ")
    Phonenumber = input("Enter delivery person's phone number: ")
    
    # insert the delivery person's details into the delivery_persons table
    sql = "INSERT INTO delivery_persons (deliveryname, Phonenumber) VALUES (%s, %s)"
    val = (deliveryname, Phonenumber)
    cursor.execute(sql, val)
    db.commit()
    
    # print a success message
    print("Delivery person registered successfully!")
    
def delivery_person_screen(phone_num):
    print("Welcome, Delivery Person!")
    print("1. View assigned orders")
    print("2. Update order status")
    print("3. Logout")
    choice = int(input("Enter your choice: "))

    if choice == 1:
        view_assigned_orders(phone_num)
    elif choice == 2:
        order_id = int(input("Enter order ID: "))
        update_status(order_id)
    elif choice == 3:
        init_screen()
    else:
        print("Invalid choice, try again.")
        delivery_person_screen(phone_num)
        
def view_assigned_orders(phone_num):
    cursor.execute("SELECT orderid, ordercity, orderstate FROM orders WHERE delivererid IN (SELECT deliveryid FROM delivery_persons WHERE Phonenumber = %s)", (phone_num,))
    orders = cursor.fetchall()
    if not orders:
        print("You have no assigned orders.")
    else:
        print("Assigned Orders:")
        for order in orders:
            print(f"Order ID: {order['orderid']}\tCity: {order['ordercity']}\tState: {order['orderstate']}")
    
def update_status(order_id):
    # Check if order exists
    query = "SELECT * FROM orders WHERE orderid=%s"
    cursor.execute(query, (order_id,))
    result = cursor.fetchone()

    if not result:
        print("Error: Order ID does not exist.")
        return

    # Check if order has already been delivered
    if result[5]:
        print("Error: Order has already been delivered.")
        return

    # Update haspaid to 1 if payment was made in cash
    if not result[3]:
        query = "UPDATE orders SET haspaid=1 WHERE orderid=%s"
        cursor.execute(query, (order_id,))
        connector.commit()

    # Update order status to delivered
    query = "UPDATE orders SET delivererid=%s WHERE orderid=%s"
    values = (current_user[0], order_id)
    cursor.execute(query, values)
    connector.commit()

    print("Order delivered successfully!")

init_screen()

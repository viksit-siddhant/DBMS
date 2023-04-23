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
    print("6. Exit")
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
        exit()

def user_login():
    print("Welcome to alldeez. Please use your credentials to login")
    username = input("Username: ")
    password = input("Password: ")
    cursor.execute("SELECT * FROM users WHERE username = %s AND pass = %s", (username, password))
    if cursor.fetchone():
        print("Login successful")
        user_mainmenu(username)
    else:
        print("Login failed, try again")
        user_login()

def user_mainmenu(user):
    print("Welcome to alldeez, " + user)
    print("1. View your orders")
    print("2. View your account details")
    print("3. View pending returns")
    print("4. Logout")
    choice = input("Please enter your choice: ")
    if choice == "1":
        view_orders(user)
    elif choice == "2":
        view_account(user)
    elif choice == "3":
        view_returns(user)
    elif choice == "4":
        init_screen()

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
    pass

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
    print("3. Add a new product")
    print("4. See geographical sales data")
    print("4. Logout")
    
    choice = input("Please enter your choice: ")
    if choice == "1":
        view_products(seller)
    elif choice == "2":
        view_selleraccount(seller)
    elif choice == "3":
        add_product(seller)
    elif choice == "4":
        cursor.execute("SELECT ordercity,orderstate, SUM(p.price) FROM orders JOIN cart ON orders.orderid = cart.orderid JOIN products p ON cart.productid = p.productid JOIN sellers s ON p.sellerid = s.sellerid WHERE s.username = %s GROUP BY ordercity, orderstate WITH ROLLUP", (seller,))
        for row in cursor.fetchall():
            print(row)
    elif choice == "5":
        init_screen()

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
    print("3. List all users")
    choice = input("Please enter your choice: ")
    if choice == "1":
        ban_user()
    elif choice == "2":
        ban_seller()

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

init_screen()
import razorpay
from email import message
from unicodedata import name
from flask import flash,Flask, redirect, render_template, request, url_for, session, jsonify, send_from_directory
import requests
import smtplib
import sqlite3
import uuid as uuid
import os
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from werkzeug.utils import secure_filename
import random
import string
import re
from datetime import datetime, timedelta
from uuid import uuid4



app = Flask(__name__)
app.secret_key = 'yash'
upload_folder = 'static/images/pics/'
VIDEO_FOLDER = 'static/videos/'
app.config['upload_folder'] = upload_folder
app.config['VIDEO_FOLDER'] = VIDEO_FOLDER
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(VIDEO_FOLDER, exist_ok=True)




def send_password_reset_email(email, temp_password):
    sender_email = "fashionholics23@gmail.com"
    sender_password = "uhvq dujm czsv umhr"
    subject = "Password Reset Request"
    message = f"Your temporary password is: {temp_password}\nPlease login and reset your password."

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, msg.as_string())
    except Exception as e:
        print(f"Error sending email: {e}")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS


# class process():
#     nam = None


# getprocess = process()


discount_ranges = {
    'level1': (100, 120),
    'level2': (90, 110),
    'level3': (80, 100)
}
  
def get_random_discount():
    return random.randint(5, 10)


@app.route('/termsandconditions')
def terms_and_conditions():
    # Serve the PDF file from the static directory
    return render_template('termsandconditions.html')

@app.route('/returnspolicy')
def returns_policy():
    # Serve the Orders and Returns Policy PDF
    return render_template('cancellationandrefund.html')

@app.route('/shippinganddelivery')
def shipping_and_delivery():
    # Serve the Orders and Returns Policy PDF
    return render_template('shippinganddelivery.html')

@app.route('/privacypolicy')
def privacy_policy():
    # Serve the Privacy Policy PDF
    return render_template('privacypolicy.html')

@app.route('/add-to-cart-combo/<string:product_id>', methods=['POST'])
def add_to_cart_combo(product_id):
    if 'user_email' not in session:
        return jsonify({"success": False, "message": "You need to log in first."})

    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()
    
    # Get details for the first product
    productdetails = cursor.execute(
        "SELECT name, price, size, img1, color FROM products WHERE sku=?", (product_id,)
    ).fetchall()


    productimage = f"../static/images/pics/{productdetails[0][3]}"
    productname = productdetails[0][0]
    productprice = float(request.form.get('productprice'))
    productsize = request.form.get('productsize')
    productcolor = productdetails[0][4]
    user_email = session['user_email']
    second_product_size = request.form.get('secondProductSize')
    second_product_color = request.form.get('productcolor')
    second_product_name = productname
    second_product_price = float(request.form.get('productprice'))  
    combined_product_name = f"{productname}, {second_product_name}"
    combined_product_size = f"{productsize}, {second_product_size}"
    combined_product_price = productprice + second_product_price
    combined_product_color = f"{productcolor}, {second_product_color}"

    cursor.execute(
        '''INSERT INTO cart 
           (productimage, productname, productsize, productprice, productquantity, totalprice, productcolor, user_email) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (productimage, combined_product_name, combined_product_size, productprice, 2, combined_product_price, combined_product_color, user_email)
    )

    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Combo items added to your cart successfully!"})


@app.route('/product-details/<product_id>', methods=['GET'])
def get_product_details(product_id):
    print("------------ Fetching Product Details -------------")
    print(f"Product ID: {product_id}")
    
    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()
    
    # Fetch the product name using SKU
    name = cursor.execute("SELECT name FROM products WHERE sku = ?", (product_id,)).fetchone()
    gender = cursor.execute("SELECT gender FROM products WHERE sku = ?", (product_id,)).fetchone()

    if not name:
        conn.close()
        return jsonify({"message": "Product not found"}), 404

    # Fetch sizes, colors, and SKUs for products with the same name
    products = cursor.execute(
        "SELECT sku, size, color, quantity FROM products WHERE name = ? and gender=?", (name[0],gender[0])
    ).fetchall()
    conn.close()
    print("-----------------------------pros---------------------------------------")
    print(products)

    if products:
        # Map sizes and colors
        size_index_map = {
            'XS': 1,
            'S': 2,
            'M': 3,
            'L': 4,
            'XL': 5,
            'XXL': 6,
            '6': 1,
            '7': 2,
            '8': 3,
            '9': 4,
            '10': 5,
            '11': 6,
            '12': 7
        }

        color_size_map = {}
        sku_links = []
        color_options_map = {}

        # Process each product entry
        for sku, size, color, quantity in products:
            sizes = size.split(',')  # Split sizes into a list
            colors = color.split(',')  # Split colors into a list
            quantities = [int(q) for q in quantity.split(',')]  # Convert quantity string to integers
            
            valid_sizes = []  # List to store sizes with available quantity
            
            # Determine valid sizes
            for size in sizes:
                index = size_index_map[size] - 1  # Get the index for the size (subtract 1 because it's 0-based)
                if quantities[index] > 0:  # Check if the quantity is greater than 0
                    valid_sizes.append(size)
            
            # Ensure correct mapping of color and size
            for c in colors:
                if c not in color_size_map:
                    color_size_map[c] = []
                color_size_map[c].extend(valid_sizes)
                color_size_map[c] = list(set(color_size_map[c]))  # Ensure uniqueness
            
            # Maintain reverse mapping for color options
            primary_color = colors[0]
            if primary_color not in color_options_map:
                color_options_map[primary_color] = colors[1:]
            
            # Generate SKU link
            sku_links.append(f"http://127.0.0.1:5000/product/{sku}")

        # Include SKU links and the reverse color mapping
        return jsonify({
            "color_size_map": color_size_map,
            "color_options_map": color_options_map,
            "sku_links": sku_links
        })
    else:
        return jsonify({"message": "No products with available stock"}), 404







@app.route('/bid', methods=['POST'])
def bid():
    bid_amount = int(request.json['bidAmount'])
    level = request.json.get('level', 'level1')
    path = request.json.get('path')
    price = request.json.get('price')
    
    # Extract product number from the path
    match = re.search(r"/product/(\d+)", path)
    if match:
        number = match.group(1)

    # Retrieve discount levels and product details from the database
    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()
    discount = cursor.execute("SELECT per1, per2, per3, size, color FROM products WHERE sku = ?", (number,)).fetchall()
    conn.close()

    level1low, level1high = map(int, discount[0][0].split('-'))
    level2low, level2high = map(int, discount[0][1].split('-'))
    level3low, level3high = map(int, discount[0][2].split('-'))

    # Randomly select a discount within each level range
    level1dis = random.randint(level1low, level1high)
    level2dis = random.randint(level2low, level2high)
    level3dis = random.randint(level3low, level3high)

    # Calculate the discount prices
    level1_price = int(price) - int(int(price) * level1dis / 100)
    level2_price = int(price) - int(int(price) * level2dis / 100)
    level3_price = int(price) - int(int(price) * level3dis / 100)
    print(level1_price)
    print(level2_price)
    print(level3_price)
    # Handle bid for each level
    if level == 'level1' and bid_amount >= level1_price:
        return jsonify({
            "message": f"🎉 Deal Locked! You've got it! Ready to secure your pick with an easy payment? 🛒💳",
            "status": "level1",
            "level2_price": level2_price,
            "level3_price": level3_price,
            "disable_bid": True
        })
    elif level == 'level2' and bid_amount >= level2_price:
        return jsonify({
            "message": f"💥 Score Big! Grab TWO stylish pieces at just ₹ {level2_price} per item! Perfectly paired, ultra-trendy, and comfy – time to elevate your style game. 👗👕✨ Are you in for this awesome deal?",
            "status": "level2",
            "level2_price": level2_price,
            "level3_price": level3_price,
            "second_product_details": {
                "sizes": discount[0][3].split(','),
                "colors": discount[0][4].split(',')
            },
            "disable_bid": True
        })
    elif level == 'level3' and bid_amount >= level3_price:
        return jsonify({
            "message": f"🚨 Last Chance Alert! 🚨 Snag this exclusive deal – ₹ {level3_price} discount on your favorite pick! 🔥 Don't let it slip away. Ready to claim it?",
            "status": "level3",
            "level2_price": level2_price,
            "level3_price": level3_price,
            "disable_bid": False
        })
    else:
        return jsonify({
            "message": "Thanks for your bid! You're almost there. How about tweaking your offer slightly to unlock a killer deal? The treasure is just within reach!",
            "status": "level3",
            "level2_price": level2_price,
            "level3_price": level3_price,
            "disable_bid": level != 'level3'
        })



             
        

@app.route('/')
def index():
    # Connect to the database
    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()
    user_email = session.get('user_email')
    if user_email:
        # Query to count items in the cart for the logged-in user
        cursor.execute("SELECT COUNT(*) FROM cart WHERE user_email = ?", (user_email,))
        cart_count = cursor.fetchone()[0]
    else:
        cart_count = 0  # If no user is logged in, the cart count is 0

    # Fetch products for each gender category
    # cursor.execute("SELECT * FROM products WHERE gender = 'Women'")
    # women_products = cursor.fetchall()

    # cursor.execute("SELECT * FROM products WHERE gender = 'Men'")
    # men_products = cursor.fetchall()

    sku = cursor.execute("SELECT sku FROM products ORDER BY RANDOM() LIMIT 5").fetchall()
    sku_list = [item[0] for item in sku]
    placeholders = ", ".join("?" for _ in sku_list)
    query = f"SELECT * FROM products WHERE sku IN ({placeholders})"
    relatedproducts = cursor.execute(query, sku_list).fetchall()
    newarrivalsmen = cursor.execute("SELECT * FROM products WHERE gender = 'Men' ORDER BY created_at DESC LIMIT 4").fetchall()
    newarrivalswomen = cursor.execute("SELECT * FROM products WHERE gender = 'Women' ORDER BY created_at DESC LIMIT 4").fetchall()
    print("---------------new arrivals--------------------")
    print(newarrivalsmen)
    print(newarrivalswomen)
    cursor.execute("SELECT name, uploadtime FROM reels")
    videos = cursor.fetchall()
    conn.close()
    
    # Render template with the fetched products
    return render_template("index.html",relatedproducts=relatedproducts,newarrivalsmen=newarrivalsmen,newarrivalswomen=newarrivalswomen, cart_count=cart_count,videos=videos)


@app.route('/cart')
def cart():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    user_email = session['user_email']

    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()
    cursor.execute("SELECT productimage, productname, productsize, productprice, productquantity, totalprice, productcolor FROM cart WHERE user_email = ?", (user_email,))
    cart_items = cursor.fetchall()
    print("-------------------cart----------------------------")
    print(cart_items)

    if user_email:
        # Query to count items in the cart for the logged-in user
        cursor.execute("SELECT COUNT(*) FROM cart WHERE user_email = ?", (user_email,))
        cart_count = cursor.fetchone()[0]
    else:
        cart_count = 0  # If no user is logged in, the cart count is 0

    # Add a flag to indicate if productname is comma-separated
    cart_items = [
        item + (',' in item[1],)  # Add True/False based on comma presence in productname
        for item in cart_items
    ]

    # Calculate subtotal (sum of totalprice)
    cursor.execute("SELECT SUM(totalprice) FROM cart WHERE user_email = ?", (user_email,))
    subtotal = cursor.fetchone()[0]
    if subtotal is None:
        subtotal = 0

    # Set shipping charges and calculate grand total
    cursor.execute("SELECT SUM(productquantity) FROM cart WHERE user_email = ?", (user_email,))
    total_quantity = cursor.fetchone()[0] or 0
    shipping_charges = 40 if total_quantity <= 3 else 70
    grand_total = subtotal + shipping_charges

    conn.close()

    return render_template('cart-variant1.html', cart_items=cart_items, subtotal=subtotal, shipping_charges=shipping_charges, grand_total=grand_total, cart_count=cart_count, total_quantity=total_quantity)


@app.route('/get-product-price', methods=['POST'])
def get_product_price():
    data = request.json
    name = data.get('productName')
    color = data.get('color')
    size = data.get('size')

    print(f"Received name: {name}, color: {color}, size: {size}")  # Debug log

    if len(name) == 2:  # If there are two products
        total_price = 0
        conn = sqlite3.connect('product.db')
        cursor = conn.cursor()
        for product_name in name:
            # Query for each product's price based on the name, color, and size
            cursor.execute("""
                SELECT price FROM products WHERE name = ? AND color = ? AND size = ?
            """, (product_name.strip(), color.strip(), size.strip()))

            price = cursor.fetchone()
            if price:
                total_price += price[0]  # Add the price of the product to total_price
            else:
                print(f"Price not found for {product_name.strip()}, {color.strip()}, {size.strip()}")

        print(f"Total price for both products: {total_price}")
    else:
    # Fetch totalprice from the products table
        conn = sqlite3.connect('product.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT price FROM products
            WHERE name = ? AND color = ? AND INSTR(size, ?) > 0
        """, (name, color, size))
        result = cursor.fetchone()
        conn.close()

        print(f"Query result: {result}")  # Debug log

        if result:
            return jsonify({'totalprice': result[0]})
        else:
            return jsonify({'error': 'Product not found'}), 404


#addtocartfromchatbotwithoffer

@app.route('/add-to-cart-offer/<string:product_id>', methods=['POST'])
def add_to_cart_offer(product_id):
    if 'user_email' not in session:
        return jsonify({"success": False, "message": "You need to log in first."})

    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()
    productdetails = cursor.execute(
        "SELECT name, price, size, img1, color FROM products WHERE sku=?", (product_id,)
    ).fetchall()

    productname = productdetails[0][0]
    productprice = float(request.form.get('productprice'))  # Should be price sent from client
    print(f"Received price: {productprice}")  # Debugging line
    productsize = request.form.get('productsize')
    productquantity = int(request.form.get('productquantity', 1))
    productimage = f"../static/images/pics/{productdetails[0][3]}"
    productcolor = productdetails[0][4]
    user_email = session['user_email']

    totalprice = productprice * productquantity

    cursor.execute(
        '''INSERT INTO cart 
           (productimage, productname, productsize, productprice, productquantity, totalprice, productcolor, user_email) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (productimage, productname, productsize, productprice, productquantity, totalprice, productcolor, user_email)
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Item added to your cart successfully!"})

@app.route('/add-to-cart/<string:id>', methods=['POST'])
def add_to_cart(id):
    print(id)
    if 'user_email' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()
    productquantity = int(request.form['productquantity'])
    productsize = request.form['productsize']
    if productsize=='XS':
        qty=0
    elif productsize=='S':
        qty=1
    elif productsize=='M':
        qty=2
    elif productsize=='L':
        qty=3
    elif productsize=='XL':
        qty=4
    elif productsize=='XXL':
        qty=5
    else:
        qty=-1
        
    curqty = cursor.execute("Select quantity from products where sku=?", (id,)).fetchone()
    print("---------------------currentqty-------------------------------")
    curqty = curqty[0].split(',')
    print(qty)
    print(curqty[qty])

    if(int(curqty[qty])<productquantity):
        flash("We currently do not have the quantity you requested in stock; please select a lower quantity.")
        return redirect(url_for('productinfo', id=id))
    else:

        productname = request.form['productname']
        productprice = float(request.form['productprice'])
        
        totalprice = productprice * productquantity
        productimage = request.form['productimage']
        productcolor = request.form['productcolor']
        user_email = session['user_email']  # Get logged-in user's email

        
        cursor.execute(
            'INSERT INTO cart (productimage, productname, productsize, productprice, productquantity, totalprice, productcolor, user_email) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (productimage, productname, productsize, productprice, productquantity, totalprice, productcolor, user_email)
        )
        conn.commit()
        conn.close()

        session['message'] = "Cart items updated!"
        return redirect(url_for('productinfo', id=id))


@app.route('/update-cart-item', methods=['POST'])
def update_cart_item():
    data = request.get_json()
    product_name = data.get('productName')
    product_size = data.get('productSize')
    product_color = data.get('productColor')
    new_quantity = data.get('newQuantity')
    new_total_price = data.get('newTotalPrice')

    # Update the cart table in the database
    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE cart
        SET productquantity = ?, totalprice = ?
        WHERE productname = ? AND productsize = ? AND productcolor = ?
    """, (new_quantity, new_total_price, product_name, product_size,product_color))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success'})


@app.route('/remove-from-cart/<productname>/<productsize>/<productcolor>', methods=['GET'])
def remove_from_cart(productname, productsize, productcolor):
    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE productname = ? AND productsize = ? AND productcolor = ?", (productname, productsize, productcolor))
    conn.commit()
    conn.close()
    return redirect(url_for('cart'))

@app.route('/clear-cart', methods=['GET'])
def clear_cart():
    # Ensure user is logged in and their email is in the session
    user_email = session.get('user_email')
    if user_email:
        conn = sqlite3.connect('product.db')
        cursor = conn.cursor()
        # Delete items from the cart only for the logged-in user
        cursor.execute("DELETE FROM cart WHERE user_email = ?", (user_email,))
        conn.commit()
        conn.close()

    return redirect(url_for('cart'))

@app.route('/contactus')
def contactus():
    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()
    user_email = session.get('user_email')
    if user_email:
        # Query to count items in the cart for the logged-in user
        cursor.execute("SELECT COUNT(*) FROM cart WHERE user_email = ?", (user_email,))
        cart_count = cursor.fetchone()[0]
    else:
        cart_count = 0  # If no user is logged in, the cart count is 0
    conn.close
    return render_template('contact-us.html', cart_count=cart_count)


@app.route('/aboutus')
def aboutus():
    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()
    user_email = session.get('user_email')
    if user_email:
        # Query to count items in the cart for the logged-in user
        cursor.execute("SELECT COUNT(*) FROM cart WHERE user_email = ?", (user_email,))
        cart_count = cursor.fetchone()[0]
    else:
        cart_count = 0  # If no user is logged in, the cart count is 0
    conn.close
    return render_template('about-us.html', cart_count=cart_count)


@app.route('/send-message', methods=['POST'])
def send_message():

    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    GMAIL_USER = "fashionholics23@gmail.com"
    GMAIL_PASSWORD = "uhvq dujm czsv umhr"
    # Get form data
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    subject = request.form['subject']
    message = request.form['message']

    # Compose email content
    email_subject = f"New Contact Us Message: {subject}"
    email_body = f"""
    Name: {name}
    Email: {email}
    Phone: {phone}
    Subject: {subject}
    Message: {message}
    """

    # Send email
    try:
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = GMAIL_USER
        msg['Subject'] = email_subject
        msg.attach(MIMEText(email_body, 'plain'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        return f"Failed to send email: {e}"
    
    return render_template('contact-us.html', message="Your message has been sent!.")

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Get the 'next' parameter from the query string
    if request.method == 'POST':
        next_page = request.form.get('next', url_for('index'))  # Default to index page if no 'next'
    else:
        next_page = request.args.get('next', url_for('index'))  # Default to index page if no 'next'

    print("------------next page----------------------")
    print(next_page)
    if request.method == 'POST':
        identifier = request.form['customer[identifier]'].lower()  # This can be email or phone
        password = request.form['customer[password]']
        
        # Connect to the database
        conn = sqlite3.connect('product.db')
        cursor = conn.cursor()

        # Check if the identifier is an email or phone
        if "@" in identifier:  # Simple check for email format
            cursor.execute("SELECT * FROM users WHERE email = ?", [identifier])
        else:
            cursor.execute("SELECT * FROM users WHERE phone = ?", [identifier])
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            # If the user exists, check the password
            if user[3] == password:  # Assuming password is in the 4th column
                # Successful login
                session['logged_in'] = True
                session['user_email'] = user[2]  # Assuming email is in the 3rd column
                session['is_admin'] = user[2] == 'fashionholics23@gmail.com' and password == 'Fashion@23'  # Set admin flag

                return redirect(next_page)  # Redirect to the original page
            else:
                # Incorrect password
                return render_template('login.html', identifier=identifier, message="Password is incorrect.")
        else:
            # User does not exist
            return redirect(url_for('register', message="Account does not exist. Please create an account."))

    return render_template('login.html')


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        
        # Connect to the database
        conn = sqlite3.connect('product.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", [email])
        user = cursor.fetchone()
        conn.close()
        
        if user:
            # Generate a temporary password or reset token
            temp_password = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))  # Replace this with a more secure random generator
            # Update the database with the temporary password
            conn = sqlite3.connect('product.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password = ? WHERE email = ?", (temp_password, email))
            conn.commit()
            conn.close()
            
            # Notify the user
            send_password_reset_email(email, temp_password)
            # Set a session variable for the alert message
            session['show_alert'] = "Login with temporary password sent to your registered email"
            return redirect(url_for('login'))  # Redirect to login page
        else:
            return render_template('forgot_password.html', message="Email not found.")
    
    return render_template('forgot_password.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = session.get('user_email')
        new_password = request.form['new_password']
        
        if email:
            # Update the database with the new password
            conn = sqlite3.connect('product.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password = ? WHERE email = ?", (new_password, email))
            conn.commit()
            conn.close()
            
            # Log the user out
            session.clear()
            
            # Redirect to login page with a message
            return redirect(url_for('login', message="Password reset successful. Please login with your new password."))
        else:
            return redirect(url_for('login', message="Session expired. Please log in again."))
    
    return render_template('Myaccount.html')





@app.route('/logout')
def logout():
    # After logging out
    session.pop('logged_in', None)
    session.pop('user_email', None)  # Clear user email if stored
    return redirect(url_for('index'))

@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/myaccount')
def myaccount():
    # Retrieve the logged-in user's email
    email = session.get('user_email')

    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()

    # Query to get only "Placed" order details from the orders table for the logged-in user
    cursor.execute("""
        SELECT 
            o.productname, 
            o.size, 
            o.color, 
            o.quantity, 
            o.totalprice, 
            o.timestamp, 
            o.razorpay_order_id,
            o.status,
            COALESCE(r.status, 'No Return') AS status,
            o.grand,
            o.link
        FROM orders o
        LEFT JOIN return r 
        ON o.razorpay_order_id = r.orderid AND o.productname = r.productname AND o.color = r.color
        WHERE o.email = ?
    """, (email,))
    order_items = cursor.fetchall()

    # Query to get address details from the useradr table for the logged-in user
    cursor.execute("""
        SELECT email, firstname, lastname, mobile, address, city, pincode, state, country 
        FROM useradr 
        WHERE email = ?
    """, (email,))
    address_data = cursor.fetchone()  # Fetch a single record

    if email:
        # Query to count items in the cart for the logged-in user
        cursor.execute("SELECT COUNT(*) FROM cart WHERE user_email = ?", (email,))
        cart_count = cursor.fetchone()[0]
    else:
        cart_count = 0  # If no user is logged in, the cart count is 0


    conn.close()

    return render_template('Myaccount.html', order_items=order_items, address_data=address_data, cart_count=cart_count)





@app.route('/product')
def product():
    productname = "Sample Product"
    productprice = 500
    message = session.pop('message', None)
    return render_template('product-layout-1.html', productname=productname, productprice=productprice, message=message)

@app.route('/send-verification-code', methods=['POST'])
def send_verification_code():
    data = request.json
    email = data.get('email')

    if not email:
        return jsonify({"success": False, "message": "Email is required."})

    # Generate a 6-character verification code
    verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    # Mock email sending (replace this with actual email sending logic)
    sender_email = "fashionholics23@gmail.com"
    sender_password = "uhvq dujm czsv umhr"
    subject = "Email Verification Code"
    message = f"Your verification code is: {verification_code}"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, msg.as_string())
            print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

    return jsonify({"success": True, "code": verification_code})

@app.route('/adduser', methods=['GET', 'POST'])
def adduser():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email'].lower()
        phone = request.form['phone']
        password = request.form['password']

        # Check if at least one of email or phone is provided
        if not email and not phone:
            return render_template('register.html', error="Please enter either an email or a phone number.")
        
        # Validate phone number (Basic validation for 10 digits)
        if phone and not re.match(r"^[0-9]{10}$", phone):
            return render_template('register.html', error="Please enter a valid 10-digit phone number.")



        # Check if the user with the same email exists
        conn = sqlite3.connect('product.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        existing_user = cursor.fetchone()
        cursor.execute("SELECT * FROM users WHERE phone=?", (phone,))
        existing_phone = cursor.fetchone()

        if existing_user:
            conn.close()
            return render_template('register.html', error="Email already exists")
        
        if existing_phone:
            conn.close()
            return render_template('register.html', error="Phone No. already exists")

        # Insert new user
        cursor.execute("INSERT INTO users (firstname, lastname, email, password, phone) VALUES (?, ?, ?, ?, ?)",
                       (firstname, lastname, email, password, phone))
        conn.commit()
        conn.close()

        return render_template('register.html', success="Registration successful! Redirecting to homepage...")
    return render_template('register.html')

@app.route('/wishlist')
def wishlist():
    if not session.get('logged_in') or not session.get('is_admin'):
        return redirect(url_for('login'))  #
    connection = sqlite3.connect('product.db')
    my_cursor = connection.cursor()
    
    # Fetch orders with conditional checks for razorpay_order_id and razorpay_payment_id
    orders = my_cursor.execute("""
    SELECT 
        firstname,
        lastname,
        email,
        mobile,
        city,
        state,
        pincode,
        payment_info,
        razorpay_order_id,
        razorpay_payment_id,
        productname,
        size,
        color,
        quantity,
        totalprice,
        address,
        status,
        (SELECT SUM(totalprice) FROM orders WHERE razorpay_order_id = o.razorpay_order_id) AS total_value,
        timestamp,
        shipping,
        grand
    FROM 
        orders o
    ORDER BY 
        timestamp DESC
    """).fetchall()

    # Group orders by razorpay_order_id
    grouped_orders = {}
    for order in orders:
        order_id = order[8]
        if order_id not in grouped_orders:
            grouped_orders[order_id] = {
                "orders": [],
                "total_value": order[17],
                "rowspan": 0
            }
        grouped_orders[order_id]["orders"].append(order)
        grouped_orders[order_id]["rowspan"] += 1

    # Transform grouped orders into a list for template rendering
    grouped_orders_list = [{"orders": data["orders"], "total_value": data["total_value"], "rowspan": data["rowspan"]} for data in grouped_orders.values()]
    
    cancel = my_cursor.execute("""
    SELECT 
        firstname,
        lastname,
        email,
        mobile,
        city,
        state,
        pincode,
        payment_info,
        razorpay_order_id,
        razorpay_payment_id,
        productname,
        size,
        color,
        quantity,
        totalprice,
        address,
        status,
        cancel
    FROM 
        orders
    WHERE 
        status = 'Cancelled'
    ORDER BY
        cancel DESC
    """).fetchall()

    print(orders)  # For debugging purposes

    # Fetch all products
    product = my_cursor.execute("SELECT * FROM products").fetchall()

    return_requests = my_cursor.execute("""
        SELECT 
            o.firstname,
            o.lastname,
            o.mobile,
            o.address,
            o.city,
            o.state,
            o.pincode,
            o.razorpay_order_id,
            o.payment_info,
            o.email,                           
            r.productname,
            r.size,
            r.color,
            r.quantity,
            r.totalprice,
            r.reason,
            r.details,
            r.image1,
            r.image2,
            r.status,
            r.timestamp
        FROM 
            orders o
        INNER JOIN 
            return r
        ON 
            o.email = r.user_email
            AND o.productname = r.productname
            AND o.razorpay_order_id = r.orderid
            AND o.color = r.color
        ORDER BY
            r.timestamp DESC
    """).fetchall()

    # Fetch counts for each status from the orders table
    my_cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'Waiting for Confirmation'")
    not_confirmed = my_cursor.fetchone()[0]

    my_cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'Confirmed and Placed'")
    placed_count = my_cursor.fetchone()[0]

    my_cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'Shipped'")
    shipped_count = my_cursor.fetchone()[0]

    my_cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'Delivered'")
    delivered_count = my_cursor.fetchone()[0]

    my_cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'Cancelled'")
    cancelled_count = my_cursor.fetchone()[0]

    # Fetch count for Returned status from the return table
    my_cursor.execute("SELECT COUNT(*) FROM return")
    returned_count = my_cursor.fetchone()[0]
    my_cursor.execute("SELECT name, uploadtime FROM reels")
    videos = my_cursor.fetchall()

    connection.commit()
    connection.close()
    
    return render_template("wishlist.html", grouped_orders=grouped_orders_list, product=product, return_requests=return_requests, cancel=cancel,placed_count=placed_count, 
                           shipped_count=shipped_count, 
                           delivered_count=delivered_count, 
                           cancelled_count=cancelled_count, 
                           returned_count=returned_count, not_confirmed=not_confirmed,videos=videos)


@app.route('/videoadddb', methods=["POST"])
def upload_video():
    if "video" not in request.files:
        flash("No file part")
        return redirect(url_for("wishlist"))

    video = request.files["video"]

    if video.filename == "":
        flash("No video selected")
        return redirect(url_for("wishlist"))

    if not allowed_file(video.filename):
        flash("File type not allowed. Please upload MP4, AVI, MOV, or MKV videos.")
        return redirect(url_for("wishlist"))

    # Save the video locally
    filename = video.filename
    video_path = os.path.join(app.config['VIDEO_FOLDER'], filename)
    video.save(video_path)

    # Save video details to the database
    upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()

    # Ensure the table exists
    cursor.execute('''CREATE TABLE IF NOT EXISTS reels (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        uploadtime TEXT NOT NULL
                      )''')

    cursor.execute("INSERT INTO reels (name, uploadtime) VALUES (?, ?)", (filename, upload_time))
    conn.commit()
    conn.close()

    flash("Video uploaded successfully!")
    return redirect(url_for("wishlist"))


@app.route('/delete_video/<filename>', methods=["POST"])
def delete_video(filename):
    # Path to the video file
    video_path = os.path.join(app.config['VIDEO_FOLDER'], filename)

    # Delete video file from local storage
    if os.path.exists(video_path):
        os.remove(video_path)
    else:
        flash("Video file not found locally!")

    # Delete video details from the database
    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reels WHERE name = ?", (filename,))
    conn.commit()
    conn.close()

    flash("Video deleted successfully!")
    return redirect(url_for("wishlist"))



@app.route('/update-order-status', methods=['POST'])
def update_order_status():
    razorpay_order_id = request.form.get('razorpay_order_id')
    productname = request.form.get('productname')
    color = request.form.get('color')
    new_status = request.form.get('status')

    if not razorpay_order_id or not productname or not color or not new_status:
        print("Missing order ID, product name, or status")
        return "Missing required parameters", 400

    # Update the database
    connection = sqlite3.connect('product.db')
    my_cursor = connection.cursor()

    # Check current status
    my_cursor.execute("""
        SELECT status, email FROM orders 
        WHERE razorpay_order_id = ? AND productname = ? AND color = ?
    """, (razorpay_order_id, productname, color))
    current_status = my_cursor.fetchone()

    if not current_status:
        connection.close()
        return "Order not found", 404

    if current_status[0] == "Cancelled":
        connection.close()
        return "Cannot update status for a cancelled order", 403

    # Update the status
    my_cursor.execute("""
        UPDATE orders 
        SET status = ? 
        WHERE razorpay_order_id = ? AND productname = ? AND color = ?
    """, (new_status, razorpay_order_id, productname, color))

    connection.commit()

    # Send email if the status is changed to "Confirmed and Placed"
    if new_status == "Confirmed and Placed":
        user_email = current_status[1]  # Fetch email from the query result
        subject = "Order Confirmation"
        body = f"""
        Dear Customer,

        Your order for {productname} in {color} has been confirmed and placed successfully.

        Order ID: {razorpay_order_id}

        Thank you for shopping with us!

        Best regards,
        Your Company Name
        """

        # Send email notification
        try:
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = "fashionholics23@gmail.com"
            sender_password = "uhvq dujm czsv umhr"

            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = user_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, user_email, msg.as_string())
            server.quit()

            print(f"Email sent to {user_email}")
        except Exception as e:
            print(f"Email notification failed: {e}")
    connection.close()

    print(f"Order ID: {razorpay_order_id}, Product: {productname}, Color: {color} updated to status: {new_status}")
    return 'Success', 200  # Respond with success so AJAX can handle it



@app.route('/update-return-status', methods=['POST'])
def update_return_status():
    razorpay_order_id = request.form.get('razorpay_order_id')
    productname = request.form.get('productname')
    color = request.form.get('color')
    new_status = request.form.get('returnstatus')

    if not razorpay_order_id or not productname or not color or not new_status:
        print(f"Missing data: order ID ({razorpay_order_id}), product name ({productname}), color ({color}), status ({new_status})")
        return jsonify({'success': False, 'message': 'Missing required fields'})

    # Update the return status in the database
    connection = sqlite3.connect('product.db')
    my_cursor = connection.cursor()

    # Check current status
    my_cursor.execute("""
        SELECT status, user_email FROM return 
        WHERE orderid = ? AND productname = ? AND color = ?
    """, (razorpay_order_id, productname, color))
    current_status = my_cursor.fetchone()

    if not current_status:
        connection.close()
        return "Order not found", 404


    my_cursor.execute("""
        UPDATE return
        SET status = ?
        WHERE orderid = ? AND productname = ? AND color = ?
    """, (new_status, razorpay_order_id, productname, color))


    connection.commit()
    # Send email if the status is changed to "Confirmed and Placed"
    if new_status == "Confirmed and Re-Placed":
        user_email = current_status[1]  # Fetch email from the query result
        subject = "Order Confirmation"
        body = f"""
        Dear Customer,

        Your order for {productname} in {color} has been confirmed and placed for return successfully.

        Order ID: {razorpay_order_id}

        Thank you for shopping with us!

        Best regards,
        Your Company Name
        """

        # Send email notification
        try:
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = "fashionholics23@gmail.com"
            sender_password = "uhvq dujm czsv umhr"

            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = user_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, user_email, msg.as_string())
            server.quit()

            print(f"Email sent to {user_email}")
        except Exception as e:
            print(f"Email notification failed: {e}")
    connection.close()

    print(f"Return status updated: {razorpay_order_id}, {productname}, {color} to {new_status}")
    return jsonify({'success': True, 'message': 'Return status updated successfully.'})


@app.route('/add-tracking-link', methods=['POST'])
def add_tracking_link():
    data = request.json
    order_id = data.get('orderId')
    product_name = data.get('productName')
    color = data.get('color')
    tracking_link = data.get('trackingLink')

    if not (order_id and product_name and color and tracking_link):
        return jsonify({'success': False, 'error': 'Missing required parameters'}), 400

    try:
        conn = sqlite3.connect('product.db')
        cursor = conn.cursor()

        # Update the link in the orders table
        cursor.execute("""
            UPDATE orders
            SET link = ?
            WHERE razorpay_order_id = ? AND productname = ? AND color = ?
        """, (tracking_link, order_id, product_name, color))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({'success': False, 'error': 'No matching order found'}), 404

        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500






@app.route('/edit-product/<sku>', methods=['GET'])
def edit_product(sku):
    # Connect to the database
    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()

    # Fetch the product data based on the SKU
    cursor.execute("SELECT * FROM products WHERE sku = ?", (sku,))
    product = cursor.fetchone()
    conn.close()

    # Pass the product data to add_product.html
    return render_template('add_product.html', product=product)

@app.route('/shopfullwidth')
def shopfullwidth():
    connection = sqlite3.connect('product.db')
    my_cursor = connection.cursor()
    lala = my_cursor.execute("SELECT * from products where gender='Men' ").fetchall()
    email = session.get('user_email')

    if email:
        # Query to count items in the cart for the logged-in user
        my_cursor.execute("SELECT COUNT(*) FROM cart WHERE user_email = ?", (email,))
        cart_count = my_cursor.fetchone()[0]
    else:
        cart_count = 0  # If no user is logged in, the cart count is 0
    connection.commit()
    connection.close()
    return render_template("shop-fullwidth.html",lala=lala, cart_count=cart_count)

@app.route('/shopfullwidth/<string:id>')
def shopfullwidthcategories(id):
    print(id)
    connection = sqlite3.connect('product.db')
    my_cursor = connection.cursor()
    lala = my_cursor.execute("SELECT * from products where category=? ",(id,)).fetchall()
    email = session.get('user_email')

    if email:
        # Query to count items in the cart for the logged-in user
        my_cursor.execute("SELECT COUNT(*) FROM cart WHERE user_email = ?", (email,))
        cart_count = my_cursor.fetchone()[0]
    else:
        cart_count = 0  # If no user is logged in, the cart count is 0
    connection.commit()
    connection.close()
    return render_template("shop-fullwidth.html",lala=lala, cart_count=cart_count)

@app.route('/shopwomen')
def shopfullwidthwomen():
    connection = sqlite3.connect('product.db')
    my_cursor = connection.cursor()
    lala = my_cursor.execute("SELECT * from products where gender='Women' ").fetchall()
    email = session.get('user_email')

    if email:
        # Query to count items in the cart for the logged-in user
        my_cursor.execute("SELECT COUNT(*) FROM cart WHERE user_email = ?", (email,))
        cart_count = my_cursor.fetchone()[0]
    else:
        cart_count = 0  # If no user is logged in, the cart count is 0
    connection.commit()
    connection.close()
    return render_template("shop-fullwidth-women.html",lala=lala, cart_count=cart_count)

@app.route('/shopwomen/<string:id>')
def shopwomencategories(id):
    connection = sqlite3.connect('product.db')
    my_cursor = connection.cursor()
    lala = my_cursor.execute("SELECT * from products where category=? ",(id,)).fetchall()
    email = session.get('user_email')

    if email:
        # Query to count items in the cart for the logged-in user
        my_cursor.execute("SELECT COUNT(*) FROM cart WHERE user_email = ?", (email,))
        cart_count = my_cursor.fetchone()[0]
    else:
        cart_count = 0  # If no user is logged in, the cart count is 0

    connection.commit()
    connection.close()
    return render_template("shop-fullwidth-women.html",lala=lala, cart_count=cart_count)

@app.route('/filter', methods=['GET'])
def filter_products():
    selected_color = request.args.get('color')
    selected_size = request.args.get('size')
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)
    current_url = request.args.get('current_url')
    selected_brands = request.args.getlist('brands')
      # Get list of selected brands
    print("-------------------------brands---------------------------------")
    print(selected_brands)

    connection = sqlite3.connect('product.db')
    my_cursor = connection.cursor()

    # Base query
    query = "SELECT * FROM products WHERE price BETWEEN ? AND ?"
    params = [min_price, max_price]

    if selected_color:
        query += " AND color = ?"
        params.append(selected_color)

    query += " AND gender = ?"
    params.append(current_url)

    # Add brand filtering to the query if brands are selected
    if selected_brands:
        query += " AND vendor IN ({})".format(', '.join(['?'] * len(selected_brands)))
        params.extend(selected_brands)

    # Execute the query and fetch filtered products
    filtered_products = my_cursor.execute(query, params).fetchall()
    connection.close()

    # Additional size filtering in Python if size is selected
    if selected_size:
        filtered_products = [
            product for product in filtered_products
            if selected_size in product[11].split(',')
        ]

    email = session.get('user_email')

    if email:
        # Query to count items in the cart for the logged-in user
        my_cursor.execute("SELECT COUNT(*) FROM cart WHERE user_email = ?", (email,))
        cart_count = my_cursor.fetchone()[0]
    else:
        cart_count = 0  # If no user is logged in, the cart count is 0

    # Render filtered products
    if current_url == 'Men':
        return render_template('shop-fullwidth.html', lala=filtered_products, min_price=min_price, max_price=max_price, color=selected_color, size=selected_size, brands=selected_brands, cart_count=cart_count)
    else:
        return render_template('shop-fullwidth-women.html', lala=filtered_products, min_price=min_price, max_price=max_price, color=selected_color, size=selected_size, brands=selected_brands, cart_count=cart_count)



#the code is to filter based on colour

@app.route('/products', methods=['GET'])
def show_products():
    selected_color = request.args.get('color')
    print('------color--------')
    print(selected_color)
    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()
    if selected_color:
        cursor.execute("SELECT * FROM products WHERE color = ? and gender='Men'", (selected_color,))
    else:
        cursor.execute("SELECT * FROM products")
    
    email = session.get('user_email')

    if email:
        # Query to count items in the cart for the logged-in user
        cursor.execute("SELECT COUNT(*) FROM cart WHERE user_email = ?", (email,))
        cart_count = cursor.fetchone()[0]
    else:
        cart_count = 0  # If no user is logged in, the cart count is 0
    
    # Fetch all matching products
    products = cursor.fetchall()
    conn.close()

    return render_template('shop-fullwidth.html', lala=products, cart_count=cart_count)

# @app.route('/buy')
# def buy():
#     connection = sqlite3.connect('database.db')
#     my_cursor = connection.cursor()
#     my_cursor.execute("Select * from sharda2")
#     lala = my_cursor.fetchall()
#     connection.close()
#     temp = ''
#     if session["successful"] != '':
#         temp = session["successful"]
#         session.pop("successful", None)
#     return render_template("Buy.html", lala=lala, temp=temp)

#this to for add product
@app.route('/productadddb', methods=['post'])
def productadddb():
    productname = request.form['productname']
    description = request.form['description']
    baseprice = request.form['base-price']
    discountpercentage1 = request.form['discountpercentage1']
    discountpercentage2 = request.form['discountpercentage2']
    discountpercentage3 = request.form['discountpercentage3']
    sku = request.form['sku']
    quantity = request.form['quantity']
    product_category_men = request.form.get('product-category-men')
    product_category_women = request.form.get('product-category-women')
    productcategory = product_category_men or product_category_women
    gender = request.form.get('gender')
    size = request.form.getlist('size')
    print(size)
    color = request.form['color'].capitalize()
    coloroption = ','.join([color.strip().capitalize() for color in request.form['coloroptions'].split(',')])
    vendor = request.form['vendor'].capitalize()
    sizes = ','.join(size)
    # colors = ','.join(color)
    # coloroptions = ','.join(coloroption)
    input1 = request.files['input1']
    input2 = request.files['input2']
    input3 = request.files['input3']
    input4 = request.files['input4']
    input5 = request.files['input5']
    
    pic = secure_filename(input1.filename)
    pic1 = str(uuid.uuid1()) + "_" + pic
    saver = request.files['input1']
    saver.save(os.path.join(app.config['upload_folder'], pic1))
    input1 = pic1

    pic = secure_filename(input2.filename)
    pic1 = str(uuid.uuid1()) + "_" + pic
    saver = request.files['input2']
    saver.save(os.path.join(app.config['upload_folder'], pic1))
    input2 = pic1

    pic = secure_filename(input3.filename)
    pic1 = str(uuid.uuid1()) + "_" + pic
    saver = request.files['input3']
    saver.save(os.path.join(app.config['upload_folder'], pic1))
    input3 = pic1

    pic = secure_filename(input4.filename)
    pic1 = str(uuid.uuid1()) + "_" + pic
    saver = request.files['input4']
    saver.save(os.path.join(app.config['upload_folder'], pic1))
    input4 = pic1

    pic = secure_filename(input5.filename)
    pic1 = str(uuid.uuid1()) + "_" + pic
    saver = request.files['input5']
    saver.save(os.path.join(app.config['upload_folder'], pic1))
    input5 = pic1

    connection = sqlite3.connect('product.db')
    my_cursor = connection.cursor()
    my_cursor.execute("INSERT INTO products (name, description, color, price, per1, per2, per3, sku, quantity, category, gender, size, img1, img2, img3, img4, img5, vendor, coloroptions, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)", (productname, description, color, baseprice, discountpercentage1, discountpercentage2, discountpercentage3, sku, quantity, productcategory, gender, sizes, input1, input2, input3, input4, input5, vendor, coloroption))
    connection.commit()
    connection.close()
    return redirect(url_for('shopfullwidth'))

@app.route('/productupdatedb/<sku>', methods=['POST'])
def productupdatedb(sku):
    updated_sku = request.form.get('sku')  # The updated SKU from the form
    productname = request.form['productname']
    description = request.form['description']
    baseprice = request.form['base-price']
    discountpercentage1 = request.form['discountpercentage1']
    discountpercentage2 = request.form['discountpercentage2']
    discountpercentage3 = request.form['discountpercentage3']
    quantity = request.form['quantity']
    product_category_men = request.form.get('product-category-men')
    product_category_women = request.form.get('product-category-women')
    productcategory = product_category_men or product_category_women
    gender = request.form.get('gender')
    size = request.form.getlist('size')
    color = request.form.getlist('color')
    vendor = request.form.get('vendor')
    sizes = ','.join(size)
    colors = ','.join(color)
    
    # Handling uploaded files for update
    input_files = []
    for i in range(1, 6):
        file = request.files.get(f'input{i}')
        if file and file.filename:
            pic = secure_filename(file.filename)
            pic1 = str(uuid.uuid1()) + "_" + pic
            file.save(os.path.join(app.config['upload_folder'], pic1))
            input_files.append(pic1)
        else:
            # Use existing images if no new file is uploaded
            input_files.append(request.form.get(f'existing_input{i}'))
    
    # Update product in the database
    connection = sqlite3.connect('product.db')
    my_cursor = connection.cursor()
    my_cursor.execute("""
        UPDATE products SET name=?, description=?, color=?, price=?, per1=?, 
        per2=?, per3=?, sku=?, quantity=?, category=?, gender=?, size=?, 
        img1=?, img2=?, img3=?, img4=?, img5=?, vendor=? WHERE sku=?
    """, (productname, description, colors, baseprice, discountpercentage1, discountpercentage2, discountpercentage3,updated_sku,
          quantity, productcategory, gender, sizes, *input_files, vendor, sku))
    connection.commit()
    connection.close()
    
    return redirect(url_for('wishlist'))

@app.route('/delete-product/<sku>', methods=['DELETE'])
def delete_product(sku):
    try:
        conn = sqlite3.connect('product.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE sku = ?", (sku,))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error deleting product: {e}")
        return jsonify({"success": False})



@app.route('/product/<string:id>')
def productinfo(id):
    logged_in = session.get('logged_in', False)
    selected_size = request.args.get('size')  # Capture the size from query params
    print("------------captured size---------------------")
    print(selected_size)

    connection = sqlite3.connect('product.db')
    my_cursor = connection.cursor()
    productname = my_cursor.execute("Select name from products where sku=?", (id,)).fetchone()
    gender = my_cursor.execute("Select gender from products where sku=?", (id,)).fetchone()
    coloroptions_str = my_cursor.execute("Select coloroptions from products where name=?", (productname[0],)).fetchone()

    

    sku = my_cursor.execute("SELECT sku FROM products WHERE gender=? ORDER BY RANDOM() LIMIT 5", (gender[0],)).fetchall()
    sku_list = [item[0] for item in sku]
    placeholders = ", ".join("?" for _ in sku_list)
    query = f"SELECT * FROM products WHERE sku IN ({placeholders})"
    relatedproducts = my_cursor.execute(query, sku_list).fetchall()
    colors = coloroptions_str[0].split(",")
    name = my_cursor.execute(
        "Select * from products where sku=?", (id,)).fetchone()

    
    description = name[1].split('\n')  # Split the description into individual lines


    sizes = my_cursor.execute(
        "Select size from products where sku=?", (id,)).fetchone()
    size_list = sizes[0].split(',') if sizes else []

    # Use the selected size if available, otherwise default to the first size
    selected_size = selected_size or (size_list[0] if size_list else None)

    data = my_cursor.execute("Select quantity from products where sku=?", (id,)).fetchone()
    print("-----------------stock---------------------")
    print(data)
    if data and data[0]:  # Ensure it's not empty or None
        if isinstance(data[0], int):  
            stock = [data[0]]  # Single integer, wrap it in a list
        elif isinstance(data[0], str) and ',' in data[0]:  
            stock = [int(s) for s in data[0].split(',')]  # Comma-separated string, split and convert
        else:
            stock = []  # Handle any unexpected cases
    else:
        stock = []  # Default to an empty list if no data or invalid data

    print("Stock:", stock)
    if len(stock)>1:
        if selected_size == 'XS':
            stock = stock[0]
        elif selected_size == 'S':
            stock = stock[1]
        elif selected_size == 'M':
            stock = stock[2]
        elif selected_size == 'L':
            stock = stock[3]
        elif selected_size == 'XL':
            stock = stock[4]
        elif selected_size == '6':
            stock = stock[0]
        elif selected_size == '7':
            stock = stock[1]
        elif selected_size == '8':
            stock = stock[2]
        elif selected_size == '9':
            stock = stock[3]
        elif selected_size == '10':
            stock = stock[4]
        elif selected_size == '11':
            stock = stock[5]
        elif selected_size == '12':
            stock = stock[6]
        else:
            stock = stock[5]
    else:
        stock = data[0]

    reviews = my_cursor.execute(
        "SELECT name, rating, title, body FROM reviews WHERE sku=? ORDER BY rating DESC LIMIT 3", 
        (id,)
    ).fetchall()

    # Calculate average rating and review count
    my_cursor.execute(
        "SELECT AVG(rating) as avg_rating, COUNT(*) as review_count FROM reviews WHERE sku=?", (id,))
    review_data = my_cursor.fetchone()
    avg_rating = round(review_data[0], 1) if review_data[0] else 0
    review_count = review_data[1] if review_data[1] else 0

    email = session.get('user_email')

    if email:
        # Query to count items in the cart for the logged-in user
        my_cursor.execute("SELECT COUNT(*) FROM cart WHERE user_email = ?", (email,))
        cart_count = my_cursor.fetchone()[0]
    else:
        cart_count = 0  # If no user is logged in, the cart count is 0

    connection.close()
    return render_template(
        "product-layout-1.html",
        name=name,
        size_list=size_list,
        id=id,
        reviews=reviews,
        avg_rating=avg_rating,
        review_count=review_count,
        colors=colors,
        relatedproducts=relatedproducts,
        stock=stock,
        selected_size=selected_size,
        cart_count=cart_count,logged_in=logged_in,description=description
    )


@app.route('/get-sku')
def get_sku():
    product_name = request.args.get('product_name')
    color = request.args.get('color')

    connection = sqlite3.connect('product.db')
    my_cursor = connection.cursor()

    # Query to fetch the SKU
    sku = my_cursor.execute(
        "SELECT sku FROM products WHERE name = ? AND color = ?", 
        (product_name, color)
    ).fetchone()

    connection.close()

    if sku:
        return jsonify({"sku": sku[0]})
    else:
        return jsonify({"sku": None})



@app.route('/submit-review-dynamic', methods=['POST'])
def submit_review_dynamic():
    if 'user_email' not in session:
        return redirect(url_for('login'))  # Redirect to login if user is not logged in

    user_email = session['user_email']
    name = request.form.get('review[author]')
    product_name = request.form.get('review[product_name]')
    color = request.form.get('review[color]')
    rating = request.form.get('review[rating]', 0)  # Default rating to 0 if not provided
    title = request.form.get('review[title]')
    body = request.form.get('review[body]')

    print(product_name)
    print(color)

    connection = sqlite3.connect('product.db')
    my_cursor = connection.cursor()

    # Fetch SKU based on product_name and color
    my_cursor.execute("""
        SELECT sku FROM products WHERE name = ? AND color = ?
    """, (product_name, color))
    result = my_cursor.fetchone()

    

    if not result:
        connection.close()
        return "SKU not found for the given product name and color", 404

    sku = result[0]

    # Insert review into the reviews table
    my_cursor.execute("""
        INSERT INTO reviews (user_email, name, rating, title, body, sku)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_email, name, rating, title, body, sku))

    connection.commit()
    connection.close()

    # Redirect back to the product page
    return redirect(url_for('productinfo', id=sku))




@app.route('/addproduct')
def addproduct():
    return render_template("add_product.html", product=None)

@app.route('/checkout')
def checkout():
    if 'user_email' not in session:
        return redirect(url_for('login'))  # Redirect to login if user is not logged in

    user_email = session['user_email']  # Get logged-in user's email

    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()
    user = cursor.execute("SELECT * FROM useradr WHERE email = ?", (user_email,))
    
    # Fetch cart items specific to the logged-in user
    cursor.execute("SELECT productimage, productname, productsize, productprice, productquantity, totalprice, productcolor FROM cart WHERE user_email = ?", (user_email,))
    cart_items = cursor.fetchall()
    
    if user_email:
        # Query to count items in the cart for the logged-in user
        cursor.execute("SELECT COUNT(*) FROM cart WHERE user_email = ?", (user_email,))
        cart_count = cursor.fetchone()[0]
    else:
        cart_count = 0  # If no user is logged in, the cart count is 0
    
    # Calculate subtotal (sum of totalprice) for the logged-in user's cart items
    cursor.execute("SELECT SUM(totalprice) FROM cart WHERE user_email = ?", (user_email,))
    subtotal = cursor.fetchone()[0]
    if subtotal is None:
        subtotal = 0

    # Set shipping charges and calculate grand total
    cursor.execute("SELECT SUM(productquantity) FROM cart WHERE user_email = ?", (user_email,))
    total_quantity = cursor.fetchone()[0] or 0
    shipping_charges = 40 if total_quantity <= 3 else 70
    grand_total = subtotal + shipping_charges

    conn.close()
    
    return render_template('checkout.html', cart_items=cart_items,userdetails=user, subtotal=subtotal, shipping_charges=shipping_charges, grand_total=grand_total, cart_count=cart_count)

@app.route('/select-color', methods=['POST'])
def select_color():
    try:
        # Parse JSON data
        data = request.get_json()
        color = data.get('color')
        sku = data.get('sku')

        if not color or not sku:
            return jsonify({"message": "Incomplete data received"}), 400

        # Connect to the database
        conn = sqlite3.connect('product.db')
        cursor = conn.cursor()

        # Get the product name for the given SKU
        name_result = cursor.execute("SELECT name FROM products WHERE sku = ?", (sku,)).fetchone()
        if not name_result:
            return jsonify({"message": "Product not found for the given SKU"}), 404
        name = name_result[0]

        # Get the SKU for the selected color and product name
        new_sku_result = cursor.execute("SELECT sku FROM products WHERE name = ? AND color = ?", (name, color)).fetchone()
        if not new_sku_result:
            return jsonify({"message": "No matching product found for the given color"}), 404
        new_sku = new_sku_result[0]

        conn.close()

        # Redirect to the productinfo route with the new SKU
        return redirect(url_for('productinfo', id=new_sku))

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return jsonify({"message": "A database error occurred", "error": str(e)}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"message": "An error occurred", "error": str(e)}), 500

@app.route('/confirm-address', methods=['POST'])
def confirm_address():
    # Get form data
    email = session.get('user_email')  # Use session email for cart filtering
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    mobile = request.form['mobile']
    address = request.form['address']
    city = request.form['city']
    pincode = request.form['pincode']
    state = request.form['state']
    country = request.form['country']
    
    # Insert into useradr table
    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()

    # Check if user with the same email exists
    cursor.execute("SELECT * FROM useradr WHERE email = ?", (email,))
    user = cursor.fetchone()

    if email:
        # Query to count items in the cart for the logged-in user
        cursor.execute("SELECT COUNT(*) FROM cart WHERE user_email = ?", (email,))
        cart_count = cursor.fetchone()[0]
    else:
        cart_count = 0  # If no user is logged in, the cart count is 0

    if user:
        # Update existing user's address details
        cursor.execute('''
            UPDATE useradr SET firstname=?, lastname=?, mobile=?, address=?, city=?, pincode=?, state=?, country=? WHERE email=?
        ''', (firstname, lastname, mobile, address, city, pincode, state, country, email))
    else:
        # Insert new user address
        cursor.execute('''
            INSERT INTO useradr (email, firstname, lastname, mobile, address, city, pincode, state, country)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (email, firstname, lastname, mobile, address, city, pincode, state, country))

    # Re-fetch updated user details to populate the form
    cursor.execute("SELECT * FROM useradr WHERE email = ?", (email,))
    userdetails = cursor.fetchone()


    # Fetch only the cart items associated with the logged-in user (session email)
    cursor.execute("SELECT productimage, productname, productsize, productprice, productquantity, totalprice, productcolor FROM cart WHERE user_email = ?", (email,))
    cart_items = cursor.fetchall()

    # Calculate subtotal (sum of totalprice for logged-in user's cart items)
    cursor.execute("SELECT SUM(totalprice) FROM cart WHERE user_email = ?", (email,))
    subtotal = cursor.fetchone()[0]
    if subtotal is None:
        subtotal = 0

    # Set shipping charges and calculate grand total
    cursor.execute("SELECT SUM(productquantity) FROM cart WHERE user_email = ?", (email,))
    total_quantity = cursor.fetchone()[0] or 0
    shipping_charges = 40 if total_quantity <= 3 else 70
    grand_total = subtotal + shipping_charges

    conn.commit()
    conn.close()

    # Send back the message with the form values and cart items
    message = "Address has been confirmed!"
    return render_template(
        'checkout.html', 
        message=message, userdetails=userdetails,
        email=email, firstname=firstname, lastname=lastname, mobile=mobile, 
        address=address, city=city, pincode=pincode, state=state, country=country, 
        cart_items=cart_items, subtotal=subtotal, shipping_charges=shipping_charges, grand_total=grand_total, cart_count=cart_count
    )


@app.route('/update-address', methods=['POST'])
def update_address():
    email = request.form['email']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    mobile = request.form['mobile']
    address = request.form['address']
    city = request.form['city']
    pincode = request.form['pincode']
    state = request.form['state']
    country = request.form['country']

    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()

  # Update address in useradr table
    cursor.execute('''
        UPDATE useradr 
        SET firstname = ?, lastname = ?, mobile = ?, address = ?, city = ?, pincode = ?, state = ?, country = ?
        WHERE email = ?
    ''', (firstname, lastname, mobile, address, city, pincode, state, country, email))

    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Address updated successfully'})


@app.route('/userdetails', methods=['POST'])
def userdetails():
    # Get form data
    email = session.get('user_email')  # Use session email for cart filtering
    password = request.form['password']
    
    # Connect to database
    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()
    
    # Initialize variables
    user = None
    cart_items = []
    subtotal = 0
    cursor.execute("SELECT SUM(productquantity) FROM cart WHERE user_email = ?", (email,))
    total_quantity = cursor.fetchone()[0] or 0
    shipping_charges = 40 if total_quantity <= 3 else 70

    # Check if the user with the provided email and password exists in users table
    truepass = cursor.execute("SELECT password FROM users WHERE email = ?", (email,)).fetchone()
    if truepass and password == truepass[0]:
        # Fetch user details from useradr table if they exist
        user = cursor.execute("SELECT * FROM useradr WHERE email = ?", (email,)).fetchone()

        # Fetch cart items for the user
        cursor.execute("SELECT productimage, productname, productsize, productprice, productquantity, totalprice, productcolor FROM cart WHERE user_email = ?", (email,))
        cart_items = cursor.fetchall()

        # Calculate subtotal (sum of totalprice for logged-in user's cart items)
        cursor.execute("SELECT SUM(totalprice) FROM cart WHERE user_email = ?", (email,))
        subtotal = cursor.fetchone()[0] or 0  # Set to 0 if subtotal is None

        # Calculate grand total
        grand_total = subtotal + shipping_charges

        conn.close()

        # Render checkout page with user details and cart information
        return render_template(
            'checkout.html',
            email=email,
            userdetails=user,
            cart_items=cart_items,
            subtotal=subtotal,
            shipping_charges=shipping_charges,
            grand_total=grand_total
        )
    else:
        # If password doesn't match, return an error
        conn.close()
        return render_template('checkout.html', error="Invalid email or password.")



@app.route('/place-order', methods=['POST'])
def place_order():
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'})

    user_email = session['user_email']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    mobile = request.form['mobile']
    address = request.form['address']
    city = request.form['city']
    state = request.form['state']
    pincode = request.form['pincode']
    payment_method = request.form.get('payment_method')  # COD or Online

    # Get optional Razorpay IDs
    if payment_method == 'Online':
        razorpay_payment_id = request.form.get('razorpay_payment_id')
        razorpay_order_id = request.form.get('razorpay_order_id')
        payment_info = "Online"
    else:
        razorpay_payment_id = None
        razorpay_order_id = f"COD-{uuid4()}"  # Generate a unique ID for COD
        payment_info = "COD"

    status = "Waiting for Confirmation"  # Static status for successful orders
    cancel_timestamp = 0
    link = "No link"
    

    # Fetch cart items for the logged-in user
    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()

    # Calculate subtotal (sum of totalprice)
    cursor.execute("SELECT SUM(totalprice) FROM cart WHERE user_email = ?", (user_email,))
    subtotal = cursor.fetchone()[0]
    if subtotal is None:
        subtotal = 0

    # Set shipping charges and calculate grand total
    cursor.execute("SELECT SUM(productquantity) FROM cart WHERE user_email = ?", (user_email,))
    total_quantity = cursor.fetchone()[0] or 0
    shipping_charges = 40 if total_quantity <= 3 else 70
    grand_total = subtotal + shipping_charges


    cursor.execute("SELECT productname, productsize, productcolor, productquantity, totalprice FROM cart WHERE user_email = ?", (user_email,))
    cart_items = cursor.fetchall()

    current_timestamp = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

    # Insert order into orders table for each cart item
    for item in cart_items:
        cursor.execute('''INSERT INTO orders (firstname, lastname, email, mobile, address, city, state, pincode, productname, size, color, quantity, totalprice, razorpay_payment_id, razorpay_order_id, payment_info, status, timestamp, shipping, grand, cancel, link)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (firstname, lastname, user_email, mobile, address, city, state, pincode, item[0], item[1], item[2], item[3], item[4], razorpay_payment_id, razorpay_order_id, payment_info, status, current_timestamp, shipping_charges, grand_total, cancel_timestamp, link))
        conn.commit()

    cursor.execute("DELETE FROM cart WHERE user_email = ?", (user_email,))
    
    print("---------------------------------------decreasing quantity=----------------------------------")
    for item in cart_items:
        product_name = item[0]  # 'productname' from cart
        sizes = item[1].split(',')  # 'productsize' from cart (comma-separated for combos)
        colors = item[2].split(',')  # 'productcolor' from cart (comma-separated for combos)
        quantity_to_decrease = item[3]  # 'productquantity' from cart

        # Check if the product_name indicates a combo (contains multiple names)
        product_names = product_name.split(',')
        if len(product_names) == len(sizes) == len(colors):  # Ensure sizes/colors match product names
            for i, name in enumerate(product_names):
                # Fetch the current quantity for each product, size, and color
                selected_size = sizes[i].strip()
                selected_color = colors[i].strip()
                cursor.execute("""
                    SELECT quantity FROM products
                    WHERE name = ? AND color = ? AND size LIKE ?
                """, (name.strip(), selected_color, f"%{selected_size}%"))
                
                current_qty = cursor.fetchone()
                if current_qty:
                    # Parse the current stock as a list
                    qty_list = list(map(int, current_qty[0].split(',')))

                    # Get the index for the current size
                    size_index = {'XS': 0, 'S': 1, 'M': 2, 'L': 3, 'XL': 4, 'XXL': 5,'6': 0,'7': 1,'8': 2,'9': 3,'10': 4,'11': 5,'12': 6}.get(selected_size)
                    print("-----------------------------------------size-index-----------------------------------------")
                    print(size_index)
                    if size_index is not None:
                        # Decrease quantity by 1
                        qty_list[size_index] -= 1

                        # Update the `qty` in the database
                        updated_qty = ','.join(map(str, qty_list))
                        cursor.execute("""
                            UPDATE products
                            SET quantity = ?
                            WHERE name = ? AND color = ?
                        """, (updated_qty, name.strip(), selected_color))
                        conn.commit()
        else:
            # Handle single-item purchase (as fallback logic)
            selected_size = sizes[0].strip()  # Single size
            selected_color = colors[0].strip()  # Single color
            cursor.execute("""
                SELECT quantity FROM products
                WHERE name = ? AND color = ? AND size LIKE ?
            """, (product_name.strip(), selected_color, f"%{selected_size}%"))

            current_qty = cursor.fetchone()
            if current_qty:
                # Parse the current stock as a list
                qty_list = list(map(int, current_qty[0].split(',')))

                # Get the index for the current size
                size_index = {'XS': 0, 'S': 1, 'M': 2, 'L': 3, 'XL': 4, 'XXL': 5,'6': 0,'7': 1,'8': 2,'9': 3,'10': 4,'11': 5,'12': 6}.get(selected_size)

                
                if size_index is not None:
                    # Decrease the quantity for the selected size
                    qty_list[size_index] -= quantity_to_decrease

                    # Update the `qty` in the database
                    updated_qty = ','.join(map(str, qty_list))
                    cursor.execute("""
                        UPDATE products
                        SET quantity = ?
                        WHERE name = ? AND color = ?
                    """, (updated_qty, product_name.strip(), selected_color))
                    conn.commit()




    
    conn.close()

    # Send email notification
    try:
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        sender_email = "fashionholics23@gmail.com"
        sender_password = "uhvq dujm czsv umhr"
        recipient_email = "fashionholics23@gmail.com"
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = "New Order Placed"
        
        body = f"Order placed by Name: {firstname} {lastname} , Email: ({user_email}), Contact: ({mobile}), OrderID: ({razorpay_order_id})."
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Email notification failed: {e}")

    return jsonify({'success': True})



@app.route('/request-return', methods=['POST'])
def request_return():
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'})

    user_email = session['user_email']
    orderid = request.form.get('orderid')
    productname = request.form.get('productname')
    size = request.form.get('size')
    color = request.form.get('color')
    quantity = request.form.get('quantity')
    totalprice = request.form.get('totalprice')
    reason = request.form.get('reason')
    details = request.form.get('details')

    input1 = None
    input2 = None

    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()

    # Check for existing return request with the same details
    cursor.execute('''
        SELECT 1 FROM return 
        WHERE user_email = ? AND orderid = ? AND productname = ? AND size = ? AND color = ?
    ''', (user_email, orderid, productname, size, color))
    existing_return = cursor.fetchone()

    if existing_return:
        conn.close()
        return jsonify({'success': False, 'message': 'Return request already exists for this product.'})


    # Save images if provided
    if reason == "Damaged Product":
        input1_file = request.files.get('input1')
        input2_file = request.files.get('input2')

        if input1_file and allowed_file(input1_file.filename):
            input1_filename = secure_filename(input1_file.filename)
            input1_path = os.path.join(app.config['upload_folder'], str(uuid.uuid4()) + "_" + input1_filename)
            input1_file.save(input1_path)
            input1 = input1_path

        if input2_file and allowed_file(input2_file.filename):
            input2_filename = secure_filename(input2_file.filename)
            input2_path = os.path.join(app.config['upload_folder'], str(uuid.uuid4()) + "_" + input2_filename)
            input2_file.save(input2_path)
            input2 = input2_path

    status = "Waiting for Confirmation"
    timestamp = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    # Insert the return request into the return table
    

    cursor.execute('''
        INSERT INTO return (user_email, productname, size, color, quantity, totalprice, reason, details, orderid, image1, image2, status, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_email, productname, size, color, quantity, totalprice, reason, details, orderid, input1, input2, status, timestamp))

    conn.commit()
    conn.close()

    # Send email notification
    try:
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        sender_email = "fashionholics23@gmail.com"
        sender_password = "uhvq dujm czsv umhr"
        recipient_email = "fashionholics23@gmail.com"

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = "Return Request Initiated"

        body = f"A Return request has been placed by Email: {user_email} for the Product: {productname} (Order ID: {orderid}). Reason: {reason}. Details: {details}."
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Email notification failed: {e}")

    return jsonify({'success': True, 'message': 'Return request has been initialized.'})


@app.route('/cancel-order', methods=['POST'])
def cancel_order():
    razorpay_order_id = request.form.get('razorpay_order_id')
    product_name = request.form.get('product_name')

    if not razorpay_order_id or not product_name:
        return jsonify({"message": "Invalid request parameters."}), 400

    connection = sqlite3.connect('product.db')
    my_cursor = connection.cursor()

    # Check the current status
    my_cursor.execute("""
        SELECT status FROM orders 
        WHERE razorpay_order_id = ? AND productname = ?
    """, (razorpay_order_id, product_name))
    result = my_cursor.fetchone()

    if result and result[0] in ['Waiting for Confirmation', 'Confirmed and Placed']:
    # Update status to 'Cancelled'
        cancel_timestamp = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        my_cursor.execute("""
            UPDATE orders 
            SET status = 'Cancelled', cancel = ? 
            WHERE razorpay_order_id = ? 
            AND productname = ? 
            AND status IN ('Waiting for Confirmation', 'Confirmed and Placed')
        """, (cancel_timestamp,razorpay_order_id, product_name))
        connection.commit()
        try:
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = "fashionholics23@gmail.com"
            sender_password = "uhvq dujm czsv umhr"
            recipient_email = "fashionholics23@gmail.com"

            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = "Order Cancelled"

            body = f"Order with ID: '{razorpay_order_id}' and Product: '{product_name}' has been cancelled by the user."
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            server.quit()
        except Exception as e:
            print(f"Email notification failed: {e}")
        connection.close()
        return jsonify({"message": "Order cancelled successfully."}), 200
    else:
        connection.close()
        return jsonify({"message": "Order cannot be cancelled. Invalid status."}), 400






@app.route('/create-order', methods=['POST'])
def create_order():
    import razorpay
    client = razorpay.Client(auth=("rzp_test_TswE6aK7d5KSvI", "iBZrxVF76YTwnUA1GL9etnDg"))

    # Set a static amount (100 paise = 1 INR) for the test order
    payment_amount = 100  # Amount in paise

    # Create Razorpay order with fixed amount
    order = client.order.create({
        "amount": payment_amount,
        "currency": "INR",
        "payment_capture": 1  # Auto-capture payment
    })

    return jsonify({
        "key_id": "rzp_test_TswE6aK7d5KSvI",
        "amount": order["amount"],
        "currency": order["currency"],
        "razorpay_order_id": order["id"]
    })


@app.route('/verify-payment', methods=['POST'])
def verify_payment():
    data = request.get_json()
    client = razorpay.Client(auth=("rzp_test_TswE6aK7d5KSvI", "iBZrxVF76YTwnUA1GL9etnDg"))
    
    try:
        # Verify signature
        client.utility.verify_payment_signature({
            'razorpay_order_id': data['razorpay_order_id'],
            'razorpay_payment_id': data['razorpay_payment_id'],
            'razorpay_signature': data['razorpay_signature']
        })
        
        # Return success along with the order and payment IDs
        return jsonify({
            "success": True,
            "razorpay_payment_id": data['razorpay_payment_id'],
            "razorpay_order_id": data['razorpay_order_id']
        })
    
    except razorpay.errors.SignatureVerificationError as e:
        print("Signature verification failed:", e)
        return jsonify({"success": False, "message": "Payment verification failed."})





if(__name__) == '__main__':
    if not os.path.exists(app.config['upload_folder']):
        os.makedirs(app.config['upload_folder'])
    app.run(debug=True)

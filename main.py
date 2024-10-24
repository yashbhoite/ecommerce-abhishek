from email import message
from unicodedata import name
from flask import Flask, redirect, render_template, request, url_for, session, jsonify
import sqlite3
import uuid as uuid
import os
import json
from werkzeug.utils import secure_filename
app = Flask(__name__)
app.secret_key = 'yash'
upload_folder = 'static/images/pics/'
app.config['upload_folder'] = upload_folder
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# class process():
#     nam = None


# getprocess = process()





@app.route('/')
def index():
    return render_template("index.html")

@app.route('/cart')
def cart():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    user_email = session['user_email']

    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()
    cursor.execute("SELECT productimage, productname, productsize, productprice, productquantity, totalprice, productcolor FROM cart WHERE user_email = ?", (user_email,))
    cart_items = cursor.fetchall()

    # Calculate subtotal (sum of totalprice)
    cursor.execute("SELECT SUM(totalprice) FROM cart WHERE user_email = ?", (user_email,))
    subtotal = cursor.fetchone()[0]
    if subtotal is None:
        subtotal = 0

    # Set shipping charges and calculate grand total
    shipping_charges = 100  # Fixed shipping charge
    grand_total = subtotal + shipping_charges

    conn.close()
    
    return render_template('cart-variant1.html', cart_items=cart_items, subtotal=subtotal, shipping_charges=shipping_charges, grand_total=grand_total)


@app.route('/add-to-cart/<string:id>', methods=['POST'])
def add_to_cart(id):
    if 'user_email' not in session:
        return redirect(url_for('login'))

    productname = request.form['productname']
    productprice = float(request.form['productprice'])
    productsize = request.form['productsize']
    productquantity = int(request.form['productquantity'])
    totalprice = productprice * productquantity
    productimage = request.form['productimage']
    productcolor = request.form['productcolor']
    user_email = session['user_email']  # Get logged-in user's email

    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()
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
    new_quantity = data.get('newQuantity')
    new_total_price = data.get('newTotalPrice')

    # Update the cart table in the database
    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE cart
        SET productquantity = ?, totalprice = ?
        WHERE productname = ? AND productsize = ?
    """, (new_quantity, new_total_price, product_name, product_size))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success'})


@app.route('/remove-from-cart/<productname>/<productsize>', methods=['GET'])
def remove_from_cart(productname, productsize):
    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE productname = ? AND productsize = ?", (productname, productsize))
    conn.commit()
    conn.close()
    return redirect(url_for('cart'))

@app.route('/clear-cart', methods=['GET'])
def clear_cart():
    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart")  # Delete all items from the cart
    conn.commit()
    conn.close()
    
    return redirect(url_for('cart'))


@app.route('/contactus')
def contactus():
    return render_template("contact-us.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['customer[email]']
        password = request.form['customer[password]']
        
        # Connect to the database
        conn = sqlite3.connect('product.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", [email])
        user = cursor.fetchone()
        conn.close()
        
        if user:
            # If the user exists, check the password
            if user[3] == password:
                # If password matches, redirect to home with success alert
                # After a successful login
                session['logged_in'] = True
                session['user_email'] = email  # You can store more user data if needed
                return redirect(url_for('index', message="Login successful!"))
            else:
                # If password is incorrect, stay on login page with email populated
                return render_template('login.html', email=email, message="Password is incorrect.")
        else:
            # If user does not exist, redirect to register page with alert
            return redirect(url_for('register', message="Account does not exist. Please create an account."))

    return render_template('login.html')


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
    return render_template("Myaccount.html")


@app.route('/product')
def product():
    productname = "Sample Product"
    productprice = 500
    message = session.pop('message', None)
    return render_template('product-layout-1.html', productname=productname, productprice=productprice, message=message)


@app.route('/adduser', methods=['GET', 'POST'])
def adduser():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        password = request.form['password']

        # Check if the user with the same email exists
        conn = sqlite3.connect('product.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()
            return render_template('register.html', error="Email already exists")

        # Insert new user
        cursor.execute("INSERT INTO users (firstname, lastname, email, password) VALUES (?, ?, ?, ?)",
                       (firstname, lastname, email, password))
        conn.commit()
        conn.close()

        return render_template('register.html', success="Registration successful! Redirecting to homepage...")
    return render_template('register.html')

@app.route('/wishlist')
def wishlist():
    return render_template("wishlist.html")

@app.route('/shopfullwidth')
def shopfullwidth():
    connection = sqlite3.connect('product.db')
    my_cursor = connection.cursor()
    lala = my_cursor.execute("SELECT * from products where gender='Men' ").fetchall()
    connection.commit()
    connection.close()
    return render_template("shop-fullwidth.html",lala=lala)

@app.route('/shopfullwidth/<string:id>')
def shopfullwidthcategories(id):
    print(id)
    connection = sqlite3.connect('product.db')
    my_cursor = connection.cursor()
    lala = my_cursor.execute("SELECT * from products where category=? ",(id,)).fetchall()
    connection.commit()
    connection.close()
    return render_template("shop-fullwidth.html",lala=lala)

@app.route('/shopwomen')
def shopfullwidthwomen():
    connection = sqlite3.connect('product.db')
    my_cursor = connection.cursor()
    lala = my_cursor.execute("SELECT * from products where gender='Women' ").fetchall()
    connection.commit()
    connection.close()
    return render_template("shop-fullwidth-women.html",lala=lala)

@app.route('/shopwomen/<string:id>')
def shopwomencategories(id):
    connection = sqlite3.connect('product.db')
    my_cursor = connection.cursor()
    lala = my_cursor.execute("SELECT * from products where category=? ",(id,)).fetchall()
    connection.commit()
    connection.close()
    return render_template("shop-fullwidth-women.html",lala=lala)

@app.route('/filter', methods=['POST'])
def filter_products():
    min_price = request.form.get('min_price', type=int)
    max_price = request.form.get('max_price', type=int)
    current_url = request.form.get('current_url')
    print('url is---------------------')
    print(current_url)
    connection = sqlite3.connect('product.db')
    my_cursor = connection.cursor()
    # Example: Filter products from the database based on the price range
    filtered_products = my_cursor.execute(
        "SELECT * FROM products WHERE price BETWEEN ? AND ? AND gender=?", (min_price, max_price,current_url)
    ).fetchall()

    # Render the filtered products back to the template
    if current_url=='Men':
        return render_template('shop-fullwidth.html', lala=filtered_products, min_price=min_price, max_price=max_price)
    else:
        return render_template('shop-fullwidth-women.html', lala=filtered_products, min_price=min_price, max_price=max_price)


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
    color = request.form.getlist('color')
    sizes = ','.join(size)
    colors = ','.join(color)
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
    my_cursor.execute("INSERT INTO products VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (productname,description,colors,baseprice,discountpercentage1,discountpercentage2,discountpercentage3,sku,quantity,productcategory,gender,sizes,input1,input2,input3,input4,input5))
    connection.commit()
    connection.close()
    return redirect(url_for('shopfullwidth'))

@app.route('/product/<string:id>')
def productinfo(id):
    connection = sqlite3.connect('product.db')
    my_cursor = connection.cursor()
    name = my_cursor.execute(
        "Select * from products where sku=?", (id,)).fetchone()
    sizes = my_cursor.execute(
        "Select size from products where sku=?", (id,)).fetchone()
    size_list = sizes[0].split(',') if sizes else []
    return render_template("product-layout-1.html", name=name,size_list=size_list,id=id)


@app.route('/addproduct')
def addproduct():
    return render_template("add_product.html")

@app.route('/checkout')
def checkout():
    if 'user_email' not in session:
        return redirect(url_for('login'))  # Redirect to login if user is not logged in

    user_email = session['user_email']  # Get logged-in user's email

    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()
    
    # Fetch cart items specific to the logged-in user
    cursor.execute("SELECT productimage, productname, productsize, productprice, productquantity, totalprice, productcolor FROM cart WHERE user_email = ?", (user_email,))
    cart_items = cursor.fetchall()
    
    # Calculate subtotal (sum of totalprice) for the logged-in user's cart items
    cursor.execute("SELECT SUM(totalprice) FROM cart WHERE user_email = ?", (user_email,))
    subtotal = cursor.fetchone()[0]
    if subtotal is None:
        subtotal = 0

    # Set shipping charges and calculate grand total
    shipping_charges = 100  # Fixed shipping charge
    grand_total = subtotal + shipping_charges

    conn.close()
    
    return render_template('checkout.html', cart_items=cart_items, subtotal=subtotal, shipping_charges=shipping_charges, grand_total=grand_total)

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

    # Fetch only the cart items associated with the logged-in user (session email)
    cursor.execute("SELECT productimage, productname, productsize, productprice, productquantity, totalprice, productcolor FROM cart WHERE user_email = ?", (email,))
    cart_items = cursor.fetchall()

    # Calculate subtotal (sum of totalprice for logged-in user's cart items)
    cursor.execute("SELECT SUM(totalprice) FROM cart WHERE user_email = ?", (email,))
    subtotal = cursor.fetchone()[0]
    if subtotal is None:
        subtotal = 0

    # Set shipping charges and calculate grand total
    shipping_charges = 100  # Fixed shipping charge
    grand_total = subtotal + shipping_charges

    conn.commit()
    conn.close()

    # Send back the message with the form values and cart items
    message = "Address has been confirmed!"
    return render_template(
        'checkout.html', 
        message=message, 
        email=email, firstname=firstname, lastname=lastname, mobile=mobile, 
        address=address, city=city, pincode=pincode, state=state, country=country, 
        cart_items=cart_items, subtotal=subtotal, shipping_charges=shipping_charges, grand_total=grand_total
    )


@app.route('/place-order', methods=['POST'])
def place_order():
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'})

    user_email = session['user_email']  # Get logged-in user's email

    # Get form data from the address form
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    mobile = request.form['mobile']
    address = request.form['address']
    city = request.form['city']
    state = request.form['state']
    pincode = request.form['pincode']

    # Fetch only the cart items for the logged-in user
    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()
    cursor.execute("SELECT productname, productsize, productcolor, productquantity, totalprice FROM cart WHERE user_email = ?", (user_email,))
    cart_items = cursor.fetchall()

    # Insert data into the orders table for each cart item
    for item in cart_items:
        productname = item[0]
        size = item[1]
        color = item[2]
        quantity = item[3]
        totalprice = item[4]

        cursor.execute('''INSERT INTO orders (firstname, lastname, email, mobile, address, city, state, pincode, productname, size, color, quantity, totalprice)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (firstname, lastname, user_email, mobile, address, city, state, pincode, productname, size, color, quantity, totalprice))

    conn.commit()
    conn.close()

    return jsonify({'success': True})





if(__name__) == '__main__':
    if not os.path.exists(app.config['upload_folder']):
        os.makedirs(app.config['upload_folder'])
    app.run(debug=True)

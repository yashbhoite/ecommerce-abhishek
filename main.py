import razorpay
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
    productprice = request.form['productprice']
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
    # Retrieve the logged-in user's email
    email = session.get('user_email')

    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()

    # Query to get only "Placed" order details from the orders table for the logged-in user
    cursor.execute("""
        SELECT productname, size, color, quantity, totalprice 
        FROM orders 
        WHERE email = ? AND status = 'Placed'
    """, (email,))
    order_items = cursor.fetchall()

    # Query to get address details from the useradr table for the logged-in user
    cursor.execute("""
        SELECT email, firstname, lastname, mobile, address, city, pincode, state, country 
        FROM useradr 
        WHERE email = ?
    """, (email,))
    address_data = cursor.fetchone()  # Fetch a single record


    conn.close()

    return render_template('myaccount.html', order_items=order_items, address_data=address_data)





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
    connection = sqlite3.connect('product.db')
    my_cursor = connection.cursor()
    orders = my_cursor.execute("SELECT firstname,lastname,email,mobile,city,state,pincode,razorpay_order_id, GROUP_CONCAT(DISTINCT productname) AS product_names, GROUP_CONCAT(DISTINCT size) AS sizes, GROUP_CONCAT(DISTINCT color) AS colors, SUM(quantity) AS total_quantity, SUM(totalprice) AS total_price FROM orders GROUP BY razorpay_order_id;").fetchall()
    print(orders)
    product = my_cursor.execute("SELECT * FROM products").fetchall()

    connection.commit()
    connection.close()
    return render_template("wishlist.html",orders=orders, product=product)

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
            if selected_size in product[12].split(',')
        ]

    # Render filtered products
    if current_url == 'Men':
        return render_template('shop-fullwidth.html', lala=filtered_products, min_price=min_price, max_price=max_price, color=selected_color, size=selected_size, brands=selected_brands)
    else:
        return render_template('shop-fullwidth-women.html', lala=filtered_products, min_price=min_price, max_price=max_price, color=selected_color, size=selected_size, brands=selected_brands)



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
    
    # Fetch all matching products
    products = cursor.fetchall()
    conn.close()

    return render_template('shop-fullwidth.html', lala=products)

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
    vendor = request.form.get('vendor')
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
    my_cursor.execute("INSERT INTO products VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (productname,description,colors,baseprice,discountpercentage1,discountpercentage2,discountpercentage3,sku,quantity,productcategory,gender,sizes,input1,input2,input3,input4,input5,vendor))
    connection.commit()
    connection.close()
    return redirect(url_for('shopfullwidth'))

@app.route('/productupdatedb/<sku>', methods=['POST'])
def productupdatedb(sku):
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
        per2=?, per3=?, quantity=?, category=?, gender=?, size=?, 
        img1=?, img2=?, img3=?, img4=?, img5=?, vendor=? WHERE sku=?
    """, (productname, description, colors, baseprice, discountpercentage1, discountpercentage2, discountpercentage3,
          quantity, productcategory, gender, sizes, *input_files, vendor, sku))
    connection.commit()
    connection.close()
    
    return redirect(url_for('shopfullwidth'))

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
    
    # Calculate subtotal (sum of totalprice) for the logged-in user's cart items
    cursor.execute("SELECT SUM(totalprice) FROM cart WHERE user_email = ?", (user_email,))
    subtotal = cursor.fetchone()[0]
    if subtotal is None:
        subtotal = 0

    # Set shipping charges and calculate grand total
    shipping_charges = 100  # Fixed shipping charge
    grand_total = subtotal + shipping_charges

    conn.close()
    
    return render_template('checkout.html', cart_items=cart_items,userdetails=user, subtotal=subtotal, shipping_charges=shipping_charges, grand_total=grand_total)

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
        message=message, userdetails=user,
        email=email, firstname=firstname, lastname=lastname, mobile=mobile, 
        address=address, city=city, pincode=pincode, state=state, country=country, 
        cart_items=cart_items, subtotal=subtotal, shipping_charges=shipping_charges, grand_total=grand_total
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
    shipping_charges = 100  # Fixed shipping charge

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
    razorpay_payment_id = request.form.get('razorpay_payment_id') if payment_method == 'Online' else None
    razorpay_order_id = request.form.get('razorpay_order_id') if payment_method == 'Online' else None
    payment_info = "COD" if payment_method == 'COD' else "Online"
    status = "Placed"  # Static status for successful orders

    # Fetch cart items for the logged-in user
    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()
    cursor.execute("SELECT productname, productsize, productcolor, productquantity, totalprice FROM cart WHERE user_email = ?", (user_email,))
    cart_items = cursor.fetchall()

    # Insert order into orders table for each cart item
    for item in cart_items:
        cursor.execute('''INSERT INTO orders (firstname, lastname, email, mobile, address, city, state, pincode, productname, size, color, quantity, totalprice, razorpay_payment_id, razorpay_order_id, payment_info, status)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (firstname, lastname, user_email, mobile, address, city, state, pincode, item[0], item[1], item[2], item[3], item[4], razorpay_payment_id, razorpay_order_id, payment_info, status))

    conn.commit()
    conn.close()

    return jsonify({'success': True})



@app.route('/cancel-order', methods=['POST'])
def cancel_order():
    # Retrieve the logged-in user's email
    email = session.get('user_email')
    if not email:
        return jsonify({'success': False, 'message': 'User not logged in'})

    # Retrieve the unique identifiers for the order to be cancelled from the request
    productname = request.json.get('productname')
    size = request.json.get('size')
    color = request.json.get('color')
    quantity = request.json.get('quantity')
    totalprice = request.json.get('totalprice')

    # Connect to the database and update the status to 'Cancelled' for the specific order
    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE orders 
        SET status = 'Cancelled' 
        WHERE email = ? AND productname = ? AND size = ? 
              AND color = ? AND quantity = ? AND totalprice = ?
    """, (email, productname, size, color, quantity, totalprice))

    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Order cancelled successfully'})






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

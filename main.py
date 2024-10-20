from email import message
from unicodedata import name
from flask import Flask, redirect, render_template, request, url_for, session
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
    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()
    cursor.execute("SELECT productimage, productname, productsize, productprice, productquantity, totalprice FROM cart")
    cart_items = cursor.fetchall()
    conn.close()
    
    return render_template('cart-variant1.html', cart_items=cart_items)

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    productname = request.form['productname']
    productprice = float(request.form['productprice'])
    productsize = request.form['productsize']
    productquantity = int(request.form['productquantity'])
    totalprice = productprice * productquantity
    productimage = request.form['productimage']  # Get the image URL from the hidden field

    # Handle file upload
    # if 'productimage' not in request.files:
    #     return render_template('product-layout-1.html', message="No file part")
    
    # file = request.files['productimage']
    
    # if file.filename == '':
    #     return render_template('product-layout-1.html', message="No selected file")

    # if file and allowed_file(file.filename):
    #     filename = secure_filename(file.filename)
    #     image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    #     file.save(image_path)
    # else:
    #     return render_template('product-layout-1.html', message="Invalid file format")

    # Insert data into the SQLite database
    conn = sqlite3.connect('product.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO cart (productimage,productname, productsize, productprice, productquantity, totalprice) VALUES (?, ?, ?, ?, ?, ?)',
        (productimage, productname, productsize, productprice, productquantity, totalprice)
    )
    conn.commit()
    conn.close()

    session['message'] = "Cart items updated!"

    return redirect(url_for('product'))

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

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/myaccount')
def myaccount():
    return render_template("Myaccount.html")


@app.route('/product')
def product():
    productname = "Sample Product"
    productprice = 500
    message = session.pop('message', None)
    return render_template('product-layout-1.html', productname=productname, productprice=productprice, message=message)


@app.route('/register')
def register():
    return render_template("register.html")

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
    return render_template("product-layout-1.html", name=name,size_list=size_list)


@app.route('/addproduct')
def addproduct():
    return render_template("add_product.html")



if(__name__) == '__main__':
    if not os.path.exists(app.config['upload_folder']):
        os.makedirs(app.config['upload_folder'])
    app.run(debug=True)

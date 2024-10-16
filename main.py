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
app.config['UPLOAD_FOLDER'] = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# class process():
#     nam = None


# getprocess = process()





@app.route('/')
def index():
    return render_template("index.html")


@app.route('/addproduct')
def addproduct():
    return render_template("add_product.html")

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

@app.route('/shop-fullwidth')
def shopfullwidth():
    return render_template("shop-fullwidth.html")



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






if(__name__) == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)

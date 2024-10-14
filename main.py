from email import message
from unicodedata import name
from flask import Flask, redirect, render_template, request, url_for, session
import sqlite3
import uuid as uuid
import os
import json
app = Flask(__name__)
app.secret_key = 'yash'
upload_folder = 'static/images/pics/'
app.config['upload_folder'] = upload_folder


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
    return render_template("cart-variant1.html")


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
    return render_template("product-layout-1.html")


@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/wishlist')
def wishlist():
    return render_template("wishlist.html")



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
    app.run(debug=True)

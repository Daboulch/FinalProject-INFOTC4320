from flask import Flask, render_template, request, flash, abort
import pygal
import requests

# To run in docker:
# docker-compose up -d
# docker-compose down

# Make a Flask application object called app
app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'your secret key'

@app.route('/')
def index():
    # Displays a seating chart that changes based on what seats are taken
    # Two buttons, one for reservation and one for admin login
    # Redirect to the reservation page or admin login page accordingly
    return render_template("index.html")

@app.route('/admin/login', methods=('GET', 'POST'))
def admin_login():
    # A link to return to the homepage
    # Form to login using admin username and admin password
    # If login is successful redirect to admin dashboard else display an error message
    pass


@app.route('/admin/dashboard')
def admin_dashboard():
    # A link to return to the homepage
    # Shows the seating chart
    # Shows total sales collected
    # Shows a list of reservations and a button to delete each reservation
    pass

@app.route('/admin/delete/<int:id>', methods=('POST',))
def delete_reservation(id):
    # Route for deleteing reservations from the admin dashboard
    pass

@app.route('/reserve/', methods=('GET', 'POST'))
def reserve():
    # A link to return to the homepage
    # Form that requires first name, last name, seat row, and seat column
    # Should probably display the seating chart with labeled row and columns
    # Creates and prints a reservation code for the user after a successful reservation
    # Insert the reservation into the SQLite database
    pass

app.run(host="0.0.0.0")
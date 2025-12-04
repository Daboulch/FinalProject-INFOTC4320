from flask import Flask, render_template, request, url_for, flash, abort, redirect
import sqlite3
import pygal
import requests

# To run in docker:
# docker-compose up -d
# docker-compose down

# Make a Flask application object called app
app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'your secret key'

def get_db_connection():
    # Create connection to the SQLite database
    conn=sqlite3.connect('reservations.db')
    conn.row_factory = sqlite3.Row
    return conn

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
    return render_template("admin_login.html")


@app.route('/admin/dashboard')
def admin_dashboard():
    # A link to return to the homepage
    # Shows the seating chart
    # Shows total sales collected
    # Shows a list of reservations and a button to delete each reservation
    return render_template("admin_dashboard.html")

@app.route('/admin/delete/<int:id>', methods=('POST',))
def delete_reservation(id):
    # Route for deleteing reservations from the admin dashboard
    pass

@app.route('/reserve/', methods=('GET', 'POST'))
def reserve():
    # A link to return to the homepage
    # Should probably display the seating chart with labeled row and columns
    conn = get_db_connection()
    reservations = conn.execute('SELECT seatRow, seatColumn FROM reservations').fetchall()
    conn.close()

    seats_taken = {(int(row['seatRow']), int(row['seatColumn'])) for row in reservations}

    # Form that requires passengerName (first name), seatRow, and seatColumn
    if request.method == 'POST':
        name = request.form['passengerName']
        row = int(request.form['seatRow'])
        column = int(request.form['seatColumn'])
        pattern = "INFOTC4320"
        eticket=""
        
        if not (0 <= row <= 11) or not (0 <= column <= 3):
            flash("Invalid seat selection!")
            return redirect(url_for('reserve'))

        max_len= max(len(name), len(pattern))
        for i in range(max_len):
            if i < len(name):
                eticket += name[i]
            if i < len(pattern):
                eticket += pattern[i]

        # Insert the reservation into the SQLite database
        conn = get_db_connection()
        conn.execute('INSERT INTO reservations (passengerName, seatRow, seatColumn, eTicketNumber) VALUES (?, ?, ?, ?)', (name, row, column, eticket))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
            
    # Creates and prints a reservation code for the user after a successful reservation
    
    return render_template("reserve.html", seats_taken=seats_taken)

app.run(host="0.0.0.0")
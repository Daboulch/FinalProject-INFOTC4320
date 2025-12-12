from flask import Flask, render_template, request, url_for, flash, abort, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

basedir = os.path.abspath(os.path.dirname(__file__))

# To run in docker:
# docker-compose up -d
# docker-compose down

# Make a Flask application object called app
app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'your secret key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'reservations.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Reservation(db.Model):
    __tablename__ = 'reservations'  # must match your table name
    id = db.Column(db.Integer, primary_key=True)
    passengerName = db.Column(db.String)
    seatRow = db.Column(db.Integer)
    seatColumn = db.Column(db.Integer)
    eTicketNumber = db.Column(db.String)
    created = db.Column(db.DateTime, default=datetime.utcnow)

class Admin(db.Model):
    __tablename__ = 'admins'  # must match your table name
    username = db.Column(db.String, primary_key=True)
    password = db.Column(db.String)

def get_cost_matrix():
    # cost matrix 12 rows x 4 columns
    return [[100, 75, 50, 100] for _ in range(12)]

@app.route('/')
def index():
    # Two buttons, one for reservation and one for admin login
    # Redirect to the reservation page or admin login page accordingly
    reservations = Reservation.query.order_by(Reservation.id.desc()).all()
    seats_taken = {(r.seatRow, r.seatColumn) for r in reservations}
    
    total_seats = 48   # 12 rows × 4 columns
    seats_available = total_seats - len(seats_taken)
    return render_template("index.html", seats_available=seats_available)

@app.route('/admin/login', methods=('GET', 'POST'))
def admin_login():
    # A link to return to the homepage
    # Form to login using admin username and admin password
    # If login is successful redirect to admin dashboard else display an error message
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        admin = Admin.query.filter_by(username=username, password=password).first()
        if admin:
            session['admin_user'] = username
            return redirect(url_for('admin_dashboard'))
        flash('Invalid admin credentials')
        return redirect(url_for('admin_login'))
    return render_template("admin_login.html")


@app.route('/admin/dashboard')
def admin_dashboard():
    # A link to return to the homepage
    # Shows the seating chart
    # Shows total sales collected
    if 'admin_user' not in session:
        flash('Please log in as admin')
        return redirect(url_for('admin_login'))

    reservations = Reservation.query.order_by(Reservation.id.desc()).all()
    
    seats_taken = {(r.seatRow, r.seatColumn) for r in reservations}

    cm = get_cost_matrix()
    total_sales = 0
    total_sales = 0
    for r in reservations:
        rr = r.seatRow
        cc = r.seatColumn
        if 0 <= rr < 12 and 0 <= cc < 4:
            total_sales += cm[rr][cc]

    return render_template('admin_dashboard.html', reservations=reservations, seats_taken=seats_taken, total_sales=total_sales)

@app.route('/admin/delete/<int:id>', methods=('POST',))
def delete_reservation(id):
    # Route for deleteing reservations from the admin dashboard
    if 'admin_user' not in session:
        abort(403)

    res = Reservation.query.get(id)
    if res:
        db.session.delete(res)
        db.session.commit()
        flash('Reservation deleted')
    return redirect(url_for('admin_dashboard'))

@app.route('/reserve/', methods=('GET', 'POST'))
def reserve():
    # A link to return to the homepage
    # Should probably display the seating chart with labeled row and columns
    reservations = Reservation.query.all()

    seats_taken = {(r.seatRow, r.seatColumn) for r in reservations}

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
        new_res = Reservation(
            passengerName=name,
            seatRow=row,
            seatColumn=column,
            eTicketNumber=eticket
        )
        db.session.add(new_res)
        db.session.commit()
        return redirect(url_for('index'))
            
    # Creates and prints a reservation code for the user after a successful reservation
    
    return render_template("reserve.html", seats_taken=seats_taken)

app.run(host="0.0.0.0")
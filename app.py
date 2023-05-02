import os

from bson import ObjectId
from flask import Flask, request, render_template, session, redirect, url_for, flash

from dbconnect import db
from movies import movie_page
from shows import show_page
from theatres import theatre_page

from datetime import datetime

app = Flask(__name__)
app.register_blueprint(theatre_page)
app.register_blueprint(movie_page)
app.register_blueprint(show_page)

app.secret_key = os.urandom(12).hex()


@app.route("/", methods=['GET'])
def index():
    error = None
    if 'username' in session:
        app.logger.debug(session['username'])
    else:
        app.logger.debug("User not logged in")
    return render_template('index.html', error=error)


def valid_login(username, password, isadmin):
    if isadmin == "admin":
        users = db.mtbs_admin.find()
    else:
        users = db.mtbs_user.find()
    for user in users:
        if user['username'] == username and user['password'] == password:
            return True
    return False


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if valid_login(request.form['username'], request.form['password'], request.form['isadmin']):
            return log_the_user_in(request.form['username'], request.form['isadmin'])
        else:
            error = 'Invalid username/password'
            app.logger.error('An error occurred', error)
    return render_template('login.html', error=error)


def log_the_user_in(username, isadmin):
    session['username'] = username
    if isadmin == "admin":
        session['isadmin'] = isadmin
    return redirect(url_for('index'))


@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    error = None
    if request.method == 'POST':
        record = {"username": request.form['username'],
                  "password": request.form['password'],
                  "isadmin": False
                  }
        x = db.mtbs_user.insert_one(record)
        print(x.inserted_id)
        return redirect(url_for('index'))
    return render_template('register_user.html', error=error)

@app.route('/book', methods=['GET', 'POST'])
def book():
    if 'username' not in session:
        flash('You were successfully logged in')
        return redirect(url_for('login'))
    show_id = request.args.get('show_id')

    error = None
    if request.method == 'POST':
        if 'username' not in session:
            flash('You were successfully logged in')
            return redirect(url_for('login'))

        show_id = request.form.get('show_id')
        tickets = request.form.get('tickets')
        x = db.mtbs_show.find_one({'_id': ObjectId(show_id)})
        if int(x['available_seats']) >= int(tickets):
            record={
                "booking_date_time":datetime.now(),
                "show_id":show_id,
                "user_id":session['username'],
                "total_amount":float((int(x['price']) * int(tickets))+((int(x['price']) * int(tickets))*0.091)),
                "no_of_tickets":int(tickets),
                "payment_id":"",
                "is_paid":False
            }
            db.mtbs_booking.insert_one(record)
            db.mtbs_show.update_one({"_id": ObjectId(show_id)},{"$set":{"available_seats":int(x['available_seats'])-int(tickets)}})
            return redirect(url_for('bookings'))

        else:
            error="Required seats not Available"

    return render_template('book.html',show_id=show_id, error=error )

@app.route('/bookings', methods=['GET', 'POST'])
def bookings():
    error = None
    data = db.mtbs_booking.find()

    return render_template('bookings.html', data=data, error=error)

@app.route('/forpayment', methods=['GET', 'POST'])
def forpayment():
    if request.method == 'POST':
        if 'username' not in session:
            flash('You were successfully logged in')
            return redirect(url_for('login'))
    id = request.args.get('id')
    data = db.mtbs_show.find_one({'_id': ObjectId(id)})
    tickets = request.form.get('tickets')

    record = {
        "user": session['username'],
        "show": ObjectId(id),
        "no_of_tickets": tickets,
        "is_paid": True}
    x = db.mtbs_booking.insert_one(record)
    print(x.inserted_id)
    return redirect(url_for('payment'), data=data, tickets=tickets)


@app.route('/payment', methods=['GET', 'POST'])
def payment():
    booking_id = request.args.get('id')

    if request.method == 'POST':
        if 'username' not in session:
            flash('You were successfully logged in')
            return redirect(url_for('login'))

        record = {"card_num": request.form['cnum'],
                  "card_name": request.form['ncard'],
                  "exp_month": request.form['month'],
                  "exp_year": request.form['year'],
                  "cvv": request.form['cvv'],
                  "booking_id":request.form['booking_id']
                  }

        x = db.mtbs_payment.insert_one(record)

        record1={"booking_id":request.form['booking_id'],
                 "user_id":session['username'],
                 }
        y=db.mtbs_ticket.insert_one(record1)
        z=db.mtbs_booking.update_one({"_id": ObjectId(request.form['booking_id'])}, {'$set': {"is_paid":True,"payment_id":y.inserted_id}})
        print(x.inserted_id)
        return redirect(url_for('bookings'))
    return render_template('payment.html',booking_id=booking_id,error=None)


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    session.pop('isadmin', None)
    return redirect(url_for('index'))


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['the_file']
        f.save('/var/www/uploads/uploaded_file.txt')


@app.route("/users")
def users_api():
    # users = get_all_users()
    users = db.mtbs_user.find()
    app.logger.debug([user for user in users])
    return [user for user in users]


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

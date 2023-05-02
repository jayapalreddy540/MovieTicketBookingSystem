from bson.objectid import ObjectId
from flask import Blueprint, session, flash
from flask import request, redirect, url_for, render_template

from dbconnect import db

theatre_page = Blueprint('theatre', __name__, template_folder='templates')


@theatre_page.route('/add_theatre', methods=['GET', 'POST'])
def add_theatre():
    error = None
    if 'username' not in session:
        flash('You were successfully logged in')
        return redirect(url_for('login'))
    if request.method == 'POST':
        record = {"name": request.form['name'],
                  "location": request.form['location'],
                  "num_seats": int(request.form['num_seats'])}

        x = db.mtbs_theatre.insert_one(record)
        print(x.inserted_id)
        return redirect(url_for('theatre.theatres'))
    return render_template('add_theatre.html', error=error)


@theatre_page.route('/theatres', methods=['GET', 'POST'])
def theatres():
    error = None
    x = db.mtbs_theatre.find()
    return render_template('theatres.html', data=x, error=error)


@theatre_page.route('/edit_theatre', methods=['GET', 'POST'])
def edit_theatre():
    error = None
    if 'username' not in session:
        flash('You were successfully logged in')
        return redirect(url_for('login'))
    id = request.args.get('id')
    x = db.mtbs_theatre.find({"_id": ObjectId(id)})
    # theatre_page.logger.debug("location:",x.location)
    if request.method == 'POST':
        record = {
            "name": request.form['name'],
            "location": request.form['location'],
            "num_seats": int(request.form['num_seats'])}

        x = db.mtbs_theatre.update_one({"_id": ObjectId(id)},{'$set': record})
        return redirect(url_for('theatre.theatres'))
    return render_template('edit_theatre.html', data=x, error=error)


@theatre_page.route('/delete_theatre', methods=['GET', 'POST'])
def delete_theatre():
    if 'username' not in session:
        flash('You were successfully logged in')
        return redirect(url_for('login'))
    id = request.args.get('id')
    result = db.mtbs_theatre.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('theatre.theatres'))

from bson.objectid import ObjectId
from flask import Blueprint, session, flash
from flask import request, redirect, url_for, render_template

from dbconnect import db
from datetime import datetime

show_page = Blueprint('show', __name__, template_folder='templates')


@show_page.route('/add_show', methods=['GET', 'POST'])
def add_show():
    error = None
    t = db.mtbs_theatre.find()
    m = db.mtbs_movie.find()
    if 'username' not in session:
        flash('You were successfully logged in')
        return redirect(url_for('login'))
    if request.method == 'POST':
        x=db.mtbs_theatre.find_one({"_id":ObjectId(request.form['theatre'])})
        print("theatres",list(x))
        print(x['num_seats'])
        sea=x['num_seats']
        record = {"movie": request.form['movie'],
                  "theatre": request.form['theatre'],
                  "mdate": request.form['mdate'],
                  "start_time": request.form['start_time'],
                  "end_time": request.form['end_time'],
                  "total_seats": int(sea),
                  "available_seats": int(sea),
                  "price": float(request.form['price'])
                  }
        da = db.mtbs_show.find(
            {"movie": request.form['movie'], "theatre": request.form['theatre'], "mdate": request.form['mdate']})
        # print("same timing",list(da))
        for i in list(da):
            st = datetime.strptime(dict(i)['start_time'], '%H:%M')
            et = datetime.strptime(dict(i)['end_time'], '%H:%M')
            fst = datetime.strptime(request.form['start_time'], '%H:%M')
            fet = datetime.strptime(request.form['end_time'], '%H:%M')
            print("st-et", st)
            print(et)
            if st <= fst <= et:
                return redirect(url_for('show.shows'))
            elif st <= fet <= et:
                return redirect(url_for('show.shows'))

        x = db.mtbs_show.insert_one(record)
        print(x.inserted_id)
        return redirect(url_for('show.shows'))
    return render_template('add_show.html', data=t, movies=m, error=error)


@show_page.route('/shows', methods=['GET', 'POST'])
def shows():
    data = []
    error = None
    x = db.mtbs_show.find()

    for d in x:
        # print(dict(d))
        # data.append(dict(d))

        # print("movie",dict(d)['movie'])
        temp = dict(d)
        y = db.mtbs_movie.find_one({"_id": ObjectId(dict(d)['movie'])})
        z = db.mtbs_theatre.find_one({"_id": ObjectId(dict(d)['theatre'])})
        if len(y) != 0 and len(z) != 0:
            temp.update({'movie_name': y['name'], 'theatre_name': z['name']})
            # print(temp)
            data.append(temp)

    return render_template('shows.html', data=data, error=error)


@show_page.route('/edit_show', methods=['GET', 'POST'])
def edit_show():
    error = None
    if 'username' not in session:
        flash('You were successfully logged in')
        return redirect(url_for('login'))
    id = request.args.get('id')
    x = db.mtbs_show.find({"_id": ObjectId(id)})

    if request.method == 'POST':
        record = {"movie": request.form['movie'],
                  "theatre": request.form['theatre'],
                  "date": request.form['date'],
                  "start_time": request.form['start_time'],
                  "end_time": request.form['end_time'],
                  "total_seats": int(request.form['total_seats']),
                  "available_seats": int(request.form['total_seats']),
                  "price": float(request.form['price'])
                  }

        x = db.mtbs_show.update_one({"_id": ObjectId(id)}, {'$set': record})
        return redirect(url_for('show.shows'))
    return render_template('edit_show.html', data=x, error=error)


@show_page.route('/delete_show', methods=['GET', 'POST'])
def delete_show():
    if 'username' not in session:
        flash('You were successfully logged in')
        return redirect(url_for('login'))
    id = request.args.get('id')
    result = db.mtbs_show.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('show.shows'))

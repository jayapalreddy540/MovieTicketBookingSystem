from bson.objectid import ObjectId
from flask import Blueprint, session, flash
from flask import request, redirect, url_for, render_template

from dbconnect import db

movie_page = Blueprint('movie', __name__, template_folder='templates')


@movie_page.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    error = None
    if 'username' not in session:
        flash('You were successfully logged in')
        return redirect(url_for('login'))
    if request.method == 'POST':
        record = {"name": request.form['name'],
                  "desc": request.form['desc'],
                  "language": request.form['language'],
                  "playtime": int(request.form['playtime'])
                  }

        x = db.mtbs_movie.insert_one(record)
        print(x.inserted_id)
        return redirect(url_for('movie.movies'))
    return render_template('add_movie.html', error=error)


@movie_page.route('/movies', methods=['GET', 'POST'])
def movies():
    error = None
    x = db.mtbs_movie.find()
    return render_template('movies.html', data=x, error=error)

@movie_page.route('/edit_movie', methods=['GET', 'POST'])
def edit_movie():
    error = None
    if 'username' not in session:
        flash('You were successfully logged in')
        return redirect(url_for('login'))
    id = request.args.get('id')
    x = db.mtbs_movie.find({"_id": ObjectId(id)})

    if request.method == 'POST':
        record = {
            "name": request.form['name'],
            "desc": request.form['desc'],
            "language": request.form['language'],
            "playtime": int(request.form['playtime'])}

        x = db.mtbs_movie.update_one({"_id": ObjectId(id)},{'$set': record})
        return redirect(url_for('movie.movies'))
    return render_template('edit_movie.html', data=x, error=error)

@movie_page.route('/delete_movie', methods=['GET', 'POST'])
def delete_movie():
    if 'username' not in session:
        flash('You were successfully logged in')
        return redirect(url_for('login'))
    id = request.args.get('id')
    result = db.mtbs_movie.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('movie.movies'))

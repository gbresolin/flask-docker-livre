import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,
    session, app)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from book.auth import login_required
from book.db import get_db

bp = Blueprint('product', __name__)


@bp.route('/search')
def search():
    db = get_db()
    searches = db.execute(
        'SELECT *'
        ' FROM product p JOIN user u ON p.author_id = u.id'
        ' where name = %s', request.form['search']
    ).fetchall()
    return render_template('product/search.html', searches=searches)


@bp.route('/')
def index():
    db = get_db()
    products = db.execute(
        'SELECT p.id, name, description, price, state, image, created, author_id, username'
        ' FROM product p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('product/home.html', products=products)


@bp.route('/inventory')
@login_required
def inventory():
    user_id = session.get('user_id')
    db = get_db()
    products = db.execute(
        'SELECT p.id, name, description, price, state, image, created, author_id, username'
        ' FROM product p JOIN user u ON p.author_id = u.id'
        ' WHERE author_id = ?'
        ' ORDER BY created DESC'
        , (user_id,)
    ).fetchall()
    return render_template('product/inventory.html', products=products)





def get_post(id, check_author=True):
    product = get_db().execute(
        'SELECT p.id, name, description, price, state, created, author_id, username'
        ' FROM product p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if product is None:
        abort(404, "Product id {0} doesn't exist.".format(id))

    if check_author and product['author_id'] != g.user['id']:
        abort(403)

    return product


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    product = get_post(id)

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        state = request.form['state']
        error = None

        if not name:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET name = ?, description = ?, price = ?, state = ?'
                ' WHERE id = ?',
                (name, description, price, state, id)
            )
            db.commit()
            return redirect(url_for('product.inventory'))

    return render_template('product/update.html', product=product)

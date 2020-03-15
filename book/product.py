from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from book.auth import login_required
from book.db import get_db

bp = Blueprint('product', __name__)


@bp.route('/')
def index():
    db = get_db()
    products = db.execute(
        'SELECT p.id, name, description, price, state, created, author_id, username'
        ' FROM product p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('product/home.html', products=products)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    state_list = ['Neuf', 'Très bon état', 'Bon état']
    category_list = ['Bandes dessinées', 'Humour']
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        state = request.form['state']
        error = None

        if not name:
            error = 'Le nom du livre est obligatoire.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO product (name, description, price, state, author_id)'
                ' VALUES (?, ?, ?, ?, ?)',
                (name, description, price, state, g.user['id'])
            )
            db.commit()
            return redirect(url_for('product.index'))

    return render_template('product/create.html', state_list=state_list)


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

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from book.auth import login_required
from book.db import get_db

bp = Blueprint('category', __name__)


@bp.route('/')
def index():
    db = get_db()
    categories = db.execute(
        'SELECT c.id, name'
        ' FROM category'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('product/home.html', categories=categories)


@bp.route('/category/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        error = None

        if not name:
            error = 'Le nom de la catégorie est obligatoire.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO category (name)'
                ' VALUES (?, ?, ?, ?, ?)',
                (name)
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

from flask import (
    Blueprint, render_template
)

bp = Blueprint('error', __name__)


# Errors
@bp.errorhandler(404)
def not_found(e):
    return render_template("error/404.html"), 404


@bp.errorhandler(403)
def forbidden(e):
    return render_template("error/403.html"), 403

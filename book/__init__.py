import os

from flask import Flask, flash, render_template, request
from werkzeug.utils import redirect, secure_filename

from book.db import get_db


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'book.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route('/about')
    def about():
        return render_template('about.html')

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import product
    app.register_blueprint(product.bp)
    app.add_url_rule('/', endpoint='home')

    app.config["IMAGE_UPLOADS"] = "book/static/uploads"
    app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF"]
    app.config["MAX_IMAGE_FILESIZE"] = 0.5 * 1024 * 1024

    error = None

    def allowed_image(filename):
        if not "." in filename:
            return False

        ext = filename.rsplit(".", 1)[1]

        if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
            return True
        else:
            error = 'Format non autorisé !'
            flash(error)

    def allowed_image_filesize(filesize):
        if int(filesize) <= app.config["MAX_IMAGE_FILESIZE"]:
            return True
        else:
            return False

    @app.route("/upload-image", methods=["GET", "POST"])
    def upload_image():
        if request.method == "POST":

            if request.files:

                if "filesize" in request.cookies:

                    if not allowed_image_filesize(request.cookies["filesize"]):
                        print("Filesize exceeded maximum limit")
                        return redirect(request.url)

                    image = request.files["image"]

                    if image.filename == "":
                        print("No filename")
                        return redirect(request.url)

                    if allowed_image(image.filename):
                        filename = secure_filename(image.filename)

                        image.save(os.path.join(app.config["IMAGE_UPLOADS"], filename))

                        print("Image saved")

                        return redirect(request.url)

                    else:
                        print("That file extension is not allowed")
                        return redirect(request.url)

        return render_template("upload_image.html")

    return app

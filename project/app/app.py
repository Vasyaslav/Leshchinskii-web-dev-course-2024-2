from flask import Flask, render_template, request, send_from_directory
from flask_login import current_user
from mysqldb import DBConnector
import mysql.connector as connector

app = Flask(__name__)
application = app
app.config.from_pyfile("config.py")

db_connector = DBConnector(app)
from auto import bp as auto_bp, init_login_manager

app.register_blueprint(auto_bp)
init_login_manager(app)

from users import bp as users_bp

app.register_blueprint(users_bp)

from visit_logs import bp as visit_logs_bp

app.register_blueprint(visit_logs_bp)


from products import bp as products_bp

app.register_blueprint(products_bp)


from user_products import bp as user_product_bp

app.register_blueprint(user_product_bp)


@app.before_request
def record_action():
    if request.endpoint == "static":
        return
    user_id = current_user.id if current_user.is_authenticated else None
    path = request.path
    connection = db_connector.connect()
    try:
        with connection.cursor(named_tuple=True, buffered=True) as cursor:
            query = "INSERT INTO visit_logs (user_id, path) VALUES (%s, %s)"
            cursor.execute(query, (user_id, path))
            connection.commit()
    except connector.errors.DatabaseError as error:
        print(error)
        connection.rollback()


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/images/<image_id>')
def image(image_id):
    with db_connector.connect().cursor(named_tuple=True) as cursor:
        cursor.execute(
            "SELECT * FROM images WHERE id = %s", [image_id]
        )
        print(cursor.statement)
        img = cursor.fetchone()
    print(img)
    print(app.config['UPLOAD_FOLDER'])
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               img.filename)


# python -m venv ve
# . ve/bin/activate -- Linux
# ve\Scripts\activate -- Windows
# pip install flask python-dotenv
# cd app
# flask run

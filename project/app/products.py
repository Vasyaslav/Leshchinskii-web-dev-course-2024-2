from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from app import db_connector
from flask_login import login_required, current_user
from auto import check_rights
import mysql.connector as connector
from werkzeug.utils import secure_filename
from os.path import join

bp = Blueprint("products", __name__, url_prefix="/products")


def get_image(product_id):
    with db_connector.connect().cursor(named_tuple=True) as cursor:
        cursor.execute(
            "SELECT * FROM images where product_id = %s", [product_id]
        )
        # print(cursor.statement)
        return cursor.fetchone()


def get_categories():
    with db_connector.connect().cursor(named_tuple=True) as cursor:
        cursor.execute(
            "SELECT * FROM categories"
        )
        # print(cursor.statement)
        return cursor.fetchall()


def get_characteristics():
    with db_connector.connect().cursor(named_tuple=True) as cursor:
        cursor.execute(
            "SELECT * FROM characteristics"
        )
        # print(cursor.statement)
        return cursor.fetchall()


@bp.route("/category")
def categories():
    return render_template("products/categories.html", categories=get_categories())


@bp.route("/category/<int:category_id>")
def category(category_id):
    with db_connector.connect().cursor(named_tuple=True) as cursor:
        cursor.execute("SELECT * FROM products WHERE category_id = %s", [category_id])
        # print(cursor.statement)
        products = cursor.fetchall()
        cursor.execute("SELECT * FROM categories WHERE id = %s", [category_id])
        # print(cursor.statement)
        category = cursor.fetchone()
    return render_template("products/category.html", products=products, category=category)


@bp.route("/new_category", methods=["POST", "GET"])
@login_required
@check_rights("create")
def new_category():
    if request.method == "POST":
        if not request.form["new_category"]:
            flash(
                "Ошибка. Проверьте, что все необходимые поля заполнены.",
                "danger",
            )
            return render_template("products/new_category.html")
        elif len(request.form["new_category"]) > 40:
            flash(
                "Ошибка. Размер названия характеристики не должно быть больше 40.",
                "danger",
            )
            return render_template("products/new_category.html")
        try:
            connection = db_connector.connect()
            with connection.cursor(named_tuple=True, buffered=True) as cursor:
                cursor.execute("INSERT INTO categories (category) VALUES(%s)", [request.form["new_category"]])
                print(cursor.statement)
                connection.commit()
            flash("Характеристика успешно создана", "success")
            return redirect(url_for("products.categories"))
        except connector.errors.DatabaseError as e:
            flash(
                f"Произошла ошибка при добавлении характеристики. Нарушение связи с базой данных. {e}",
                "danger",
            )
            connection.rollback()
    return render_template("products/new_category.html")


@bp.route("/<int:category_id>/delete_category", methods=["POST"])
@login_required
@check_rights("delete")
def delete_category(category_id):
    connection = db_connector.connect()
    with connection.cursor(named_tuple=True) as cursor:
        query = "DELETE FROM categories WHERE id = %s"
        cursor.execute(query, [category_id])
        connection.commit()
    flash("Категория успешно удалена", "success")
    return redirect(url_for("products.categories"))


@bp.route("/characteristic")
@login_required
@check_rights("create")
def characteristics():
    return render_template("products/characteristics.html", characteristics=get_characteristics())


@bp.route("/new_characteristic", methods=["POST", "GET"])
@login_required
@check_rights("create")
def new_characteristic():
    if request.method == "POST":
        if not request.form["new_characteristic"]:
            flash(
                "Ошибка. Проверьте, что все необходимые поля заполнены.",
                "danger",
            )
            return render_template("products/new_characteristic.html")
        elif len(request.form["new_characteristic"]) > 40:
            flash(
                "Ошибка. Размер названия характеристики не должно быть больше 40.",
                "danger",
            )
            return render_template("products/new_characteristic.html")
        try:
            connection = db_connector.connect()
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO characteristics (characteristic) VALUES(%s)", [request.form["new_characteristic"]])
                print(cursor.statement)
                connection.commit()
            flash("Характеристика успешно создана", "success")
            return redirect(url_for("products.characteristics"))
        except connector.errors.DatabaseError:
            flash(
                f"Произошла ошибка при добавлении характеристики. Нарушение связи с базой данных.",
                "danger",
            )
            connection.rollback()
    return render_template("products/new_characteristic.html")


@bp.route("/<int:characteristic_id>/delete_characteristic", methods=["POST"])
@login_required
@check_rights("delete")
def delete_characteristic(characteristic_id):
    connection = db_connector.connect()
    with connection.cursor(named_tuple=True) as cursor:
        query = "DELETE FROM characteristics WHERE id = %s"
        cursor.execute(query, [characteristic_id])
        connection.commit()
    flash("Характеристика успешно удалена", "success")
    return redirect(url_for("products.characteristics"))


@bp.route ("/<int:product_id>")
def product(product_id):
    with db_connector.connect().cursor(named_tuple=True) as cursor:
        query = ("SELECT products.*, category FROM `products` LEFT JOIN categories "
                 "on products.category_id = categories.id where products.id = %s")
        cursor.execute(query, [product_id])
        print(cursor.statement)
        product_data = cursor.fetchone()
        print(product_data)
        query = ("SELECT characteristic, value FROM `product-characteristic` JOIN characteristics "
                 "on characteristics.id = characteristic_id WHERE product_id = %s")
        cursor.execute(query, [product_id])
        print(cursor.statement)
        product_characteristics_data = cursor.fetchall()
    return render_template("products/product.html", product=product_data, characteristics=product_characteristics_data, image=get_image(product_data.id))


@bp.route("/<int:product_id>/delete_product", methods=["POST"])
@login_required
@check_rights("delete")
def delete_product(product_id):
    connection = db_connector.connect()
    with connection.cursor(named_tuple=True) as cursor:
        query = "DELETE FROM products WHERE id = %s"
        cursor.execute(query, (product_id,))
        connection.commit()
    flash("Товар успешно удален", "success")
    return redirect(url_for("products.categories"))


@bp.route("/new_product", methods=["POST", "GET"])
@check_rights("create")
def new_product():
    product_name = ""
    characteristics = get_characteristics()
    print(characteristics)
    categories = get_categories()
    print(categories)
    if request.method == "POST":
        print(request.form)
        if not request.form["product_name"]:
            flash(
                "Ошибка. Проверьте, что все необходимые поля заполнены.",
                "danger",
            )
            return render_template("products/new_product.html", characteristics=characteristics, categories=categories)
        elif len(request.form["product_name"]) >= 60:
            flash(
                "Ошибка. Размер названия товара не должно быть больше 60.",
                "danger",
            )
            return render_template("products/new_product.html", characteristics=characteristics, categories=categories)
        try:
            connection = db_connector.connect()
            with connection.cursor(named_tuple=True, buffered=True) as cursor:
                # Добавление товара в таблицу с товарами
                query = ("INSERT INTO products (name, description, price, category_id) "
                         "VALUES(%(product_name)s, %(product_description)s, %(product_price)s, %(product_category_select)s)")
                cursor.execute(query, request.form)
                print(cursor.statement)
                # Получение id текущего товара
                query = ("SELECT id from products where name = %(product_name)s "
                         "and description = %(product_description)s and price = %(product_price)s "
                         "and category_id = %(product_category_select)s")
                cursor.execute(query, request.form)
                current_product_id = cursor.fetchone().id
                print(cursor.statement)
                # Добавление значений в таблицу с товарами-характеристиками
                for key in request.form:
                    if key.split("_")[1] == "characteristic" and key.split("_")[2] == "input" and request.form[key]:
                        if len(request.form[key]) >= 50:
                            flash("Длина значения характеристики должна быть меньше 50 символов","danger")
                            return render_template("products/new_product.html")
                        product_characteristic_data = [current_product_id, 
                                                         request.form[f"product_characteristic_select_{key.split('_')[3]}"], 
                                                         request.form[key]]
                        query = ("INSERT INTO `product-characteristic` "
                                 "VALUES(%s, %s, %s)")
                        cursor.execute(query, product_characteristic_data)
                        print(cursor.statement)
                # Добавление изображения в таблицу изображений и в папку media\images
                if "product_img" in request.files and secure_filename(request.files["product_img"].filename):
                    print("image =", request.files)
                    product_image = request.files["product_img"]
                    print(type(secure_filename(product_image.filename)), type(product_image.mimetype), type(current_product_id))
                    image_data = [secure_filename(product_image.filename), product_image.mimetype, current_product_id]
                    query = ("INSERT INTO images (filename, mimetype, product_id) "
                             "VALUES(%s, %s, %s)")
                    cursor.execute(query, image_data)
                    product_image.save(join(current_app.config["UPLOAD_FOLDER"], image_data[0]))
                    print(cursor.statement)
                connection.commit()
            flash("Товар успешно добавлен", "success")
            return redirect(url_for("products.new_product"))
        except connector.errors.DatabaseError as e:
            flash(
                f"Произошла ошибка при добавлении характеристики. Нарушение связи с базой данных. {e}",
                "danger",
            )
            connection.rollback()
    return render_template("products/new_product.html", characteristics=characteristics, categories=categories)


@bp.route("/<int:product_id>/edit_product", methods=["POST", "GET"])
@check_rights("update_product")
def edit_product(product_id):
    product_name = ""
    characteristics = get_characteristics()
    print(characteristics)
    categories = get_categories()
    print(categories)
    with db_connector.connect().cursor(named_tuple=True, buffered=True) as cursor:
        cursor.execute("SELECT * FROM products WHERE id = %s", [product_id])
        product_data = cursor.fetchone()
        cursor.execute("SELECT * FROM characteristics JOIN `product-characteristic` ON "
                       "characteristics.id = `product-characteristic`.characteristic_id "
                       "WHERE product_id = %s", [product_id])
        current_characteristics = cursor.fetchall()
    print("Тек. характеристики:", current_characteristics)
    print("Характеристики:", characteristics)
    if request.method == "POST":
        print(request.form)
        if not request.form["product_name"]:
            flash(
                "Ошибка. Проверьте, что все необходимые поля заполнены.",
                "danger",
            )
            return render_template("products/new_product.html", characteristics=characteristics, categories=categories)
        elif len(request.form["product_name"]) >= 60:
            flash(
                "Ошибка. Размер названия товара не должно быть больше 60.",
                "danger",
            )
            return render_template("products/new_product.html", characteristics=characteristics, categories=categories)
        try:
            connection = db_connector.connect()
            with connection.cursor(named_tuple=True, buffered=True) as cursor:
                # Добавление товара в таблицу с товарами
                query = ("INSERT INTO products (name, description, price, category_id) "
                         "VALUES(%(product_name)s, %(product_description)s, %(product_price)s, %(product_category_select)s)")
                cursor.execute(query, request.form)
                print(cursor.statement)
                # Получение id текущего товара
                query = ("SELECT id from products where name = %(product_name)s "
                         "and description = %(product_description)s and price = %(product_price)s "
                         "and category_id = %(product_category_select)s")
                cursor.execute(query, request.form)
                current_product_id = cursor.fetchone().id
                print(cursor.statement)
                # Добавление значений в таблицу с товарами-характеристиками
                for key in request.form:
                    if key.split("_")[1] == "characteristic" and key.split("_")[2] == "input" and request.form[key]:
                        if len(request.form[key]) >= 50:
                            flash("Длина значения характеристики должна быть меньше 50 символов","danger")
                            return render_template("products/new_product.html")
                        product_characteristic_data = [current_product_id, 
                                                         request.form[f"product_characteristic_select_{key.split('_')[3]}"], 
                                                         request.form[key]]
                        query = ("INSERT INTO `product-characteristic` "
                                 "VALUES(%s, %s, %s)")
                        cursor.execute(query, product_characteristic_data)
                        print(cursor.statement)
                # Добавление изображения в таблицу изображений и в папку media\images
                if "product_img" in request.files:
                    product_image = request.files["product_img"]
                    print(type(secure_filename(product_image.filename)), type(product_image.mimetype), type(current_product_id))
                    image_data = [secure_filename(product_image.filename), product_image.mimetype, current_product_id]
                    query = ("INSERT INTO images (filename, mimetype, product_id) "
                             "VALUES(%s, %s, %s)")
                    cursor.execute(query, image_data)
                    product_image.save(join(current_app.config["UPLOAD_FOLDER"], image_data[0]))
                    print(cursor.statement)
                connection.commit()
            flash("Товар успешно добавлен", "success")
            return redirect(url_for("products.new_product"))
        except connector.errors.DatabaseError as e:
            flash(
                f"Произошла ошибка при добавлении характеристики. Нарушение связи с базой данных. {e}",
                "danger",
            )
            connection.rollback()
    return render_template("products/edit_product.html", characteristics=characteristics,
     categories=categories, current_characteristics=current_characteristics,
     product_data=product_data)

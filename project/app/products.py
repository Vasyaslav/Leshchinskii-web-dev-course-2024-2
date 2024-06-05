from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db_connector
from flask_login import login_required, current_user
from auto import check_rights
import mysql.connector as connector

bp = Blueprint("products", __name__, url_prefix="/products")


@bp.route("/category")
def category():
    with db_connector.connect().cursor(named_tuple=True) as cursor:
        cursor.execute(
            "SELECT * FROM categories"
        )
        print(cursor.statement)
        categories = cursor.fetchall()
    return render_template("products/category.html", categories=categories)


@bp.route("/characteristic")
#@check_rights("create")
def characteristic():
    with db_connector.connect().cursor(named_tuple=True) as cursor:
        cursor.execute(
            "SELECT * FROM characteristics"
        )
        print(cursor.statement)
        characteristics = cursor.fetchall()
    return render_template("products/characteristic.html", characteristics=characteristics)


@bp.route("/new_product", methods=["POST", "GET"])
#@check_rights("create")
def new_product():
    products_data = {}
    with db_connector.connect().cursor(named_tuple=True) as cursor:
        cursor.execute(
            "SELECT * FROM characteristics"
        )
        print(cursor.statement)
        characteristics = cursor.fetchall()
    with db_connector.connect().cursor(named_tuple=True) as cursor:
        cursor.execute(
            "SELECT * FROM categories"
        )
        print(cursor.statement)
        categories = cursor.fetchall()
    if request.method == "POST":
        pass
    return render_template("products/new_product.html", characteristics=characteristics, categories=categories)


@bp.route("/new_characteristic", methods=["POST", "GET"])
#@check_rights("create")
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
            return redirect(url_for("products.category"))
        except connector.errors.DatabaseError as e:
            flash(
                f"Произошла ошибка при добавлении характеристики. Нарушение связи с базой данных. {e}",
                "danger",
            )
            connection.rollback()
    return render_template("products/new_characteristic.html")


@bp.route("/new_category", methods=["POST", "GET"])
#@check_rights("create")
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
            return redirect(url_for("products.category"))
        except connector.errors.DatabaseError as e:
            flash(
                f"Произошла ошибка при добавлении характеристики. Нарушение связи с базой данных. {e}",
                "danger",
            )
            connection.rollback()
    return render_template("products/new_category.html")

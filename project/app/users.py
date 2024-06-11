from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from app import db_connector
from flask_login import login_required, current_user
from auto import check_rights
import mysql.connector as connector
from werkzeug.utils import secure_filename
import csv
from os.path import join
from os import remove

bp = Blueprint("users", __name__, url_prefix="/users")


def get_roles():
    result = []
    with db_connector.connect().cursor(named_tuple=True) as cursor:
        cursor.execute("SELECT * FROM roles")
        result = cursor.fetchall()
    return result


@bp.route("/<int:user_id>/delete", methods=["POST"])
@login_required
@check_rights("delete_user")
def delete_user(user_id):
    # Удаление пользователя
    print(12)
    connection = db_connector.connect()
    with connection.cursor(named_tuple=True) as cursor:
        query = "DELETE FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        connection.commit()
    flash("Учетная запись успешно удалена", "success")
    return redirect(url_for("index"))


@bp.route("/reg", methods=["POST", "GET"])
def reg():
    # Регистрация пользователя
    user_data = {}
    if request.method == "POST":
        fields = (
            "login",
            "password",
            "first_name",
            "middle_name",
            "last_name",
        )
        user_data = {field: request.form[field] or None for field in fields}
        try:
            connection = db_connector.connect()
            with connection.cursor(named_tuple=True) as cursor:
                query = (
                    "INSERT INTO users (login, password_hash, first_name, middle_name, last_name, role_id) VALUES "
                    "(%(login)s, SHA2(%(password)s, 256), %(first_name)s, %(middle_name)s, %(last_name)s, 1)"
                )
                cursor.execute(query, user_data)
                print(cursor.statement)
                connection.commit()
            flash("Учетная запись успешно создана", "success")
            return redirect(url_for("users.index"))
        except connector.errors.DatabaseError:
            flash(
                "Произошла ошибка при создании записи. Проверьте, что все необходимые поля заполнены",
                "danger",
            )
            connection.rollback()
    return render_template("users/reg.html", user_data=user_data, roles=get_roles())


@bp.route("/<int:user_id>/profile", methods=["POST", "GET"])
@login_required
@check_rights("read")
def profile(user_id):
    # Отображение профиля пользователя
    user_data = {}
    with db_connector.connect().cursor(named_tuple=True, buffered=True) as cursor:
        query = "SELECT * FROM users WHERE id = %s"
        cursor.execute(query, [user_id])
        user_data = cursor.fetchone()
        if user_data is None:
            flash("Пользователя нет в базе данных", "danger")
            return redirect(url_for("users.index"))
        query = ("SELECT * FROM products LEFT JOIN `user-product` on products.id = `user-product`.product_id "
                 "WHERE `user-product`.user_id = %s")
        cursor.execute(query, [current_user.id])
        user_products = cursor.fetchall()
    # Обработка загрузки списка товаров из csv файла
    if request.method == "POST":
        if "user_products_csv" in request.files and secure_filename(request.files["user_products_csv"].filename):
            try:
                connection = db_connector.connect()
                with connection.cursor(named_tuple=True, buffered=True) as cursor:
                    user_products_csv = request.files["user_products_csv"]
                    # Временное сохранение файла для извлечения информации
                    user_products_csv.save(join(current_app.config["UPLOAD_FOLDER"], secure_filename(user_products_csv.filename)))
                    print(join(current_app.config["UPLOAD_FOLDER"], secure_filename(user_products_csv.filename)))
                    with open(join(current_app.config["UPLOAD_FOLDER"], secure_filename(user_products_csv.filename)), newline='') as f:
                        text = list(csv.reader(f, delimiter=','))
                        print(text)
                        if len(list(text)) > 1:
                            print(text)
                            # Очистка текущих товаров в корзине
                            cursor.execute("DELETE FROM `user-product` WHERE user_id = %s", [user_id])
                            connection.commit()
                            print(cursor.statement)
                            for row in text:
                                print(1, row)
                            for row in list(text)[1:]:
                                cursor.execute("SELECT id FROM products WHERE name = %s", [row[0]])
                                product_id = cursor.fetchone()
                                print(row, cursor.statement)
                                # Проверка существует ли такой товар в БД
                                if product_id:
                                    # Добавление товаров в таблицу user-product
                                    query = ("INSERT INTO `user-product` (user_id, product_id, amount) "
                                             "VALUES(%s, %s, %s)")
                                    cursor.execute(query, [current_user.id, product_id.id, row[2]])
                                    print(', '.join(row))
                                else:
                                    flash(f"Произошла ошибка при добавлении товара, не найден в базе данных. {e}", "danger")
                                    connection.rollback()
                    connection.commit()
                    # Удаление файла
                    remove(join(current_app.config["UPLOAD_FOLDER"], secure_filename(user_products_csv.filename)))
                    flash("Список загружен", "success")
                    return redirect(url_for("users.profile", user_id=user_id))
            except connector.errors.DatabaseError as e:
                flash(
                    f"Произошла ошибка при добавлении товара. Нарушение связи с базой данных. {e}",
                    "danger",
                )
                connection.rollback()
    return render_template("users/profile.html", user_data=user_data, user_products=user_products)


@bp.route("/<int:user_id>/edit", methods=["POST", "GET"])
@login_required
@check_rights("update_user")
def edit(user_id):
    # Изменение данных пользователя
    user_data = {}
    with db_connector.connect().cursor(named_tuple=True, buffered=True) as cursor:
        query = (
            "SELECT first_name, middle_name, last_name, role_id "
            "FROM users WHERE id = %s"
        )
        cursor.execute(query, [user_id])
        user_data = cursor.fetchone()
        if user_data is None:
            flash("Пользователя нет в базе данных", "danger")
            return redirect(url_for("index"))
    if request.method == "POST":
        fields = ["first_name", "middle_name", "last_name", "role_id"]
        user_data = {field: request.form[field] or None for field in fields}
        user_data["id"] = user_id
        try:
            connection = db_connector.connect()
            with connection.cursor(named_tuple=True) as cursor:
                field_assignments = ", ".join(
                    [f"{field} = %({field})s" for field in fields]
                )
                query = f"UPDATE users SET {field_assignments} " "WHERE id = %(id)s"
                print(query)
                cursor.execute(query, user_data)
                connection.commit()
            flash("Учетная запись успешно изменена", "success")
            return redirect(url_for("users.profile", user_id=current_user.id))
        except connector.errors.DatabaseError as error:
            flash(f"Произошла ошибка при изменении записи: {error}", "danger")
            connection.rollback()
    return render_template("users/edit.html", user_data=user_data, roles=get_roles())


@bp.route("/<int:user_id>/new_order", methods=["POST", "GET"])
@login_required
@check_rights("read")
def new_order(user_id):
    # Отображение текущего заказа и возможность его "покупки"
    orders_data = {}
    sum_price = 0.0
    with db_connector.connect().cursor(named_tuple=True) as cursor:
        query = ("SELECT products.*, amount from products LEFT JOIN `user-product` "
                 "ON products.id = `user-product`.product_id WHERE "
                 "`user-product`.user_id = %s")
        cursor.execute(query, [user_id])
        orders_data = cursor.fetchall()
        print(orders_data)
    if not orders_data:
        flash("Нет товаров в корзине", "danger")
        return redirect(url_for("users.profile", user_id=user_id))
    for product in orders_data:
        sum_price += product.price * product.amount
    if request.method == "POST":
        try:
            connection = db_connector.connect()
            with connection.cursor(buffered=True, named_tuple=True) as cursor:
                # Добавление id пользователя в таблицу с заказами
                query = ("INSERT INTO orders (user_id) "
                         "VALUES(%s)")
                cursor.execute(query, [user_id])
                print(cursor.statement)
                # Поиск id нашего заказа
                query = ("SELECT id FROM orders WHERE "
                         "user_id = %s")
                cursor.execute(query, [user_id])
                order_id = cursor.fetchall()
                order_id = sorted(order_id, reverse=True, key=lambda x: x.id)[0]
                print(cursor.statement)
                print(order_id)
                # Добавление записей в связующую таблицу `order-product`
                for product in orders_data:
                    query = ("INSERT INTO `order-product` (product_id, order_id, amount) "
                             "VALUES(%s, %s, %s)")
                    cursor.execute(query, [product.id, order_id[0], product.amount])
                    print(cursor.statement)
                # Очистка текущего списка покупок
                query = ("DELETE FROM `user-product` WHERE "
                         "user_id = %s")
                cursor.execute(query, [user_id])
                print(cursor.statement)
                connection.commit()
            flash("Заказ оформлен", "success")
            return redirect(url_for("users.profile", user_id=user_id))
        except connector.errors.DatabaseError as e:
            flash(
                f"Произошла ошибка при оформлении заказа. Проверьте, что все необходимые поля заполнены {e}sss",
                "danger",
            )
            connection.rollback()
    return render_template("users/new_order.html", orders_data=orders_data, sum_price=sum_price)


@bp.route("/<int:user_id>/previous_orders")
@login_required
@check_rights("read")
def previous_orders(user_id):
    # Отображение предыдущих заказов
    orders_data = {}
    with db_connector.connect().cursor(buffered=True, named_tuple=True) as cursor:
        query = ('SELECT products.name, products.description, products.price, amount, orders.id from products LEFT JOIN `order-product` '
                 'ON products.id = `order-product`.product_id LEFT JOIN orders '
                 'ON `order-product`.order_id = orders.id WHERE '
                 'orders.user_id = %s')
        cursor.execute(query, [user_id])
        for product_data in cursor.fetchall():
            if str(product_data.id) in orders_data:
                orders_data[str(product_data.id)].append(product_data)
            else:
                orders_data[str(product_data.id)] = [product_data]
        print(cursor.statement)
        print(orders_data)
    return render_template("users/previous_orders.html", orders_data=orders_data)

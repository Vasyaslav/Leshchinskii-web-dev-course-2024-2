from io import BytesIO
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file
from app import db_connector
from flask_login import login_required, current_user
from auto import check_rights
import mysql.connector as connector

bp = Blueprint("user_products", __name__, url_prefix="/user_products")


@bp.route("/<int:user_id>/<int:product_id>/add", methods=["POST"])
@check_rights("update_user")
def buy_product(user_id, product_id):
    data = {"user_id": user_id, "product_id": product_id}
    try:
        connection = db_connector.connect()
        with connection.cursor(named_tuple=True, buffered=True) as cursor:
            # Проверка есть ли такие товары в корзине у пользователя
            query = ("SELECT * FROM `user-product` WHERE "
                     "user_id = %(user_id)s AND product_id = %(product_id)s")
            cursor.execute(query, data)
            current_user_product = cursor.fetchone()
            print(current_user_product)
            # Добавление записи если таких товаров пользователь не добавлял в корзину
            if not current_user_product:
                query = ("INSERT INTO `user-product` (user_id, product_id, amount) "
                         "VALUES(%(user_id)s, %(product_id)s, 1)")
                cursor.execute(query, data)
            # Иначе обновление количества
            else:
                data["amount"] = int(current_user_product.amount) + 1
                query = ("UPDATE `user-product` SET amount = %(amount)s "
                         "WHERE user_id = %(user_id)s AND product_id = %(product_id)s")
                cursor.execute(query, data)
            print(cursor.statement)
            connection.commit()
        flash("Товар добавлен в корзину", "success")
        return redirect(url_for("users.profile", user_id=current_user.id))
    except connector.errors.DatabaseError as e:
        flash(
            f"Произошла ошибка при добавлении товара в корзину. Нарушение связи с базой данных. {e}",
            "danger",
        )
        connection.rollback()
    return redirect(url_for('user_products.buy_product', user_id=user_id, product_id=product_id))


@bp.route("/<int:user_id>/<int:product_id>/delete", methods=["POST"])
@check_rights("update_user")
def delete_product(user_id, product_id):
    data = {"user_id": user_id, "product_id": product_id}
    try:
        connection = db_connector.connect()
        with connection.cursor(named_tuple=True, buffered=True) as cursor:
            # Проверка есть ли такие товары в корзине у пользователя
            query = ("SELECT * FROM `user-product` WHERE "
                     "user_id = %(user_id)s AND product_id = %(product_id)s")
            cursor.execute(query, data)
            current_user_product = cursor.fetchone()
            print(current_user_product)
            # Удаление записи
            if current_user_product:
                query = ("DELETE FROM `user-product` WHERE "
                         "user_id = %(user_id)s AND product_id = %(product_id)s")
                cursor.execute(query, data)
                print(cursor.statement)
                connection.commit()
            else:
                flash("Произошла ошибка при удалении товара из корзины. Товар не найден в корзине.", "danger")
                return redirect(url_for("users.profile", user_id=current_user.id))
        flash("Товар удалён из корзины", "success")
    except connector.errors.DatabaseError as e:
        flash(
            f"Произошла ошибка при удалении товара из корзины. Нарушение связи с базой данных. {e}",
            "danger",
        )
        connection.rollback()
    return redirect(url_for("users.profile", user_id=current_user.id))


@bp.route("/<int:user_id>/<int:product_id>/add_amount", methods=["POST"])
@check_rights("update_user")
def add_amount(user_id, product_id):
    data = {"user_id": user_id, "product_id": product_id}
    try:
        connection = db_connector.connect()
        with connection.cursor(named_tuple=True, buffered=True) as cursor:
            # Проверка есть ли такие товары в корзине у пользователя
            query = ("SELECT * FROM `user-product` WHERE "
                     "user_id = %(user_id)s AND product_id = %(product_id)s")
            cursor.execute(query, data)
            current_user_product = cursor.fetchone()
            print(current_user_product)
            # Увеличение кол-ва товара в корзине
            if current_user_product:
                data["amount"] = int(current_user_product.amount) + 1
                query = ("UPDATE `user-product` SET amount = %(amount)s "
                         "WHERE user_id = %(user_id)s AND product_id = %(product_id)s")
                cursor.execute(query, data)
                connection.commit()
            else:
                flash("Произошла ошибка при увеличении кол-ва товара. Товар не найден в корзине.", "danger")
                return redirect(url_for("users.profile", user_id=current_user.id))
    except connector.errors.DatabaseError as e:
        flash(
            f"Произошла ошибка при увеличении кол-ва товара. Нарушение связи с базой данных. {e}",
            "danger",
        )
        connection.rollback()
    return redirect(url_for("users.profile", user_id=current_user.id))


@bp.route("/<int:user_id>/<int:product_id>/reduce_amount", methods=["POST"])
@check_rights("update_user")
def reduce_amount(user_id, product_id):
    data = {"user_id": user_id, "product_id": product_id}
    try:
        connection = db_connector.connect()
        with connection.cursor(named_tuple=True, buffered=True) as cursor:
            # Проверка есть ли такие товары в корзине у пользователя
            query = ("SELECT * FROM `user-product` WHERE "
                     "user_id = %(user_id)s AND product_id = %(product_id)s")
            cursor.execute(query, data)
            current_user_product = cursor.fetchone()
            print(current_user_product)
            # Удаление записи
            if current_user_product:
                if current_user_product.amount == 1:
                    flash("Кол-во товара равно 1, для удаления нажмите на кнопку 'Удалить' напротив товара.", "info")
                    return redirect(url_for("users.profile", user_id=current_user.id))
                else:
                    data["amount"] = int(current_user_product.amount) - 1
                    query = ("UPDATE `user-product` SET amount = %(amount)s "
                             "WHERE user_id = %(user_id)s AND product_id = %(product_id)s")
                    cursor.execute(query, data)
                connection.commit()
            else:
                flash("Произошла ошибка при уменьшении кол-ва товара. Товар не найден в корзине.", "danger")
                return redirect(url_for("users.profile", user_id=current_user.id))
    except connector.errors.DatabaseError as e:
        flash(
            f"Произошла ошибка при уменьшении кол-ва товара. Нарушение связи с базой данных. {e}",
            "danger",
        )
        connection.rollback()
    return redirect(url_for("users.profile", user_id=current_user.id))


@bp.route("export.csv")
def user_products_export():
    with db_connector.connect().cursor(named_tuple=True, buffered=True) as cursor:
        query = ('SELECT name AS "Товар", amount AS "Количество", price AS "Цена_за_штуку" '
                 'FROM products LEFT JOIN `user-product` on products.id = `user-product`.product_id '
                 'WHERE `user-product`.user_id = %s')
        cursor.execute(query, [current_user.id])
        print(cursor.statement)
        user_product_data = cursor.fetchall()
        result = ""
        fields = ["Товар", "Цена_за_штуку", "Количество"]
        result += ",".join(fields) + "\n"
        for record in user_product_data:
            result += ",".join([str(getattr(record, field)) for field in fields]) + "\n"
    return send_file(
        BytesIO(result.encode()),
        as_attachment=True,
        mimetype="text/csv",
        download_name="user_products_export.csv",
    )
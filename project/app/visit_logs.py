from io import BytesIO
from flask import Blueprint, render_template, request, send_file
from flask_login import current_user, login_required
from app import db_connector
from auto import check_rights
from math import ceil

bp = Blueprint("visit_logs", __name__, url_prefix="/visit_logs")
MAX_PER_PAGE = 10


@bp.route("/")
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    with db_connector.connect().cursor(named_tuple=True) as cursor:
        if current_user.can("view_logs"):
            query = (
                "SELECT user_id, last_name, first_name, middle_name, "
                "path, visit_logs.created_at AS created_at "
                "FROM visit_logs LEFT JOIN users ON visit_logs.user_id = users.id "
                f"LIMIT {MAX_PER_PAGE} OFFSET {(page - 1) * MAX_PER_PAGE}"
            )
            cursor.execute(query)
            visit_logs = cursor.fetchall()
            query = "SELECT COUNT(*) as count FROM visit_logs"
            cursor.execute(query)
            record_count = cursor.fetchone().count
        else:
            query = (
                "SELECT user_id, last_name, first_name, middle_name, "
                "path, visit_logs.created_at AS created_at "
                "FROM visit_logs LEFT JOIN users ON visit_logs.user_id = users.id "
                "WHERE visit_logs.user_id = %s "
                f"LIMIT {MAX_PER_PAGE} OFFSET {(page - 1) * MAX_PER_PAGE}"
            )
            cursor.execute(query, (current_user.id,))
            visit_logs = cursor.fetchall()
            query = (
                "SELECT COUNT(*) as count FROM visit_logs "
                "WHERE visit_logs.user_id = %s "
            )
            cursor.execute(query, (current_user.id,))
            record_count = cursor.fetchone().count

        page_count = ceil(record_count / MAX_PER_PAGE)
        pages = range(max(1, page - 3), min(page_count, page + 3) + 1)
    return render_template(
        "visit_logs/index.html",
        visit_logs=visit_logs,
        page=page,
        pages=pages,
        page_count=page_count,
    )


@bp.route("users_stats")
@check_rights("view_logs")
def users_stats():
    with db_connector.connect().cursor(named_tuple=True) as cursor:
        query = (
            "SELECT user_id, last_name, first_name, middle_name, "
            "COUNT(*) AS entries_counter "
            "FROM visit_logs LEFT JOIN users ON visit_logs.user_id = users.id "
            "GROUP BY user_id "
        )
        cursor.execute(query)
        # print(1)
        # print(cursor.statement)
        users_stats = cursor.fetchall()
        # print(users_stats)
    return render_template("visit_logs/users_stats.html", users_stats=users_stats)


@bp.route("user_export.csv")
def user_export():
    with db_connector.connect().cursor(named_tuple=True) as cursor:
        query = (
            "SELECT user_id, last_name, first_name, middle_name, "
            "COUNT(*) AS entries_counter "
            "FROM visit_logs LEFT JOIN users ON visit_logs.user_id = users.id "
            "GROUP BY user_id "
        )
        cursor.execute(query)
        print(cursor.statement)
        users_stats = cursor.fetchall()
        result = ""
        fields = ["last_name", "first_name", "middle_name", "entries_counter"]
        none_values = ["не", "авторизованный", "пользователь"]
        result += ",".join(fields) + "\n"
        for record in users_stats:
            if record.user_id is None:
                result += (
                    ",".join(none_values) + "," + str(record.entries_counter) + "\n"
                )
                continue
            result += ",".join([str(getattr(record, field)) for field in fields]) + "\n"
    return send_file(
        BytesIO(result.encode()),
        as_attachment=True,
        mimetype="text/csv",
        download_name="user_export.csv",
    )


@bp.route("paths_stats")
@check_rights("view_logs")
def paths_stats():
    with db_connector.connect().cursor(named_tuple=True, buffered=True) as cursor:
        query = 'select path, count(*) as "count" from visit_logs group by path'
        cursor.execute(query)
        paths_stats = cursor.fetchall()
    return render_template("visit_logs/paths_stats.html", paths_stats=paths_stats)


@bp.route("path_export.csv")
def path_export():
    with db_connector.connect().cursor(named_tuple=True, buffered=True) as cursor:
        query = 'select path as "Страница", count(*) as "Количество_посещений" from visit_logs group by path'
        cursor.execute(query)
        print(cursor.statement)
        users_stats = cursor.fetchall()
        result = ""
        fields = ["Страница", "Количество_посещений"]
        result += ",".join(fields) + "\n"
        for record in users_stats:
            result += ",".join([str(getattr(record, field)) for field in fields]) + "\n"
    return send_file(
        BytesIO(result.encode()),
        as_attachment=True,
        mimetype="text/csv",
        download_name="path_export.csv",
    )

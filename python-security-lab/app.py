import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from database import init_db, get_db

app = Flask(__name__)
app.secret_key = os.environ.get("LAB_SECRET_KEY", "development-only-change-me")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

init_db()


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/<mode>")
def lab(mode):
    if mode not in ("vulnerable", "patched"):
        return redirect(url_for("index"))
    return render_template("lab.html", mode=mode)


@app.post("/<mode>/login")
def login(mode):
    if mode not in ("vulnerable", "patched"):
        return ("Not found", 404)

    username = request.form.get("username", "")
    password = request.form.get("password", "")
    conn = get_db()

    if mode == "vulnerable":
        query = (
            "SELECT id, username, email FROM users "
            f"WHERE username = '{username}' AND password = '{password}'"
        )
        user = conn.execute(query).fetchone()
    else:
        user = conn.execute(
            "SELECT id, username, email FROM users "
            "WHERE username = ? AND password = ?",
            (username, password),
        ).fetchone()

    conn.close()

    if user:
        session[f"{mode}_user_id"] = user["id"]
        flash(f"Вы вошли как {user['username']}.", "success")
    else:
        flash("Неверное имя пользователя или пароль.", "error")

    return redirect(url_for("lab", mode=mode))


@app.get("/<mode>/profile/<int:user_id>")
def profile(mode, user_id):
    if mode not in ("vulnerable", "patched"):
        return ("Not found", 404)

    if mode == "patched":
        current_user_id = session.get("patched_user_id")
        if current_user_id is None:
            return jsonify(error="Требуется авторизация"), 401
        if current_user_id != user_id:
            return jsonify(error="Доступ запрещён"), 403

    conn = get_db()
    user = conn.execute(
        "SELECT id, username, email FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    conn.close()

    if user is None:
        return jsonify(error="Пользователь не найден"), 404
    return jsonify(dict(user))


@app.post("/<mode>/logout")
def logout(mode):
    if mode not in ("vulnerable", "patched"):
        return ("Not found", 404)
    session.pop(f"{mode}_user_id", None)
    flash("Вы вышли из системы.", "success")
    return redirect(url_for("lab", mode=mode))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
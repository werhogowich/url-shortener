import os
import random
import string
import socket
import psycopg2
from flask import Flask, request, redirect, render_template_string, jsonify

app = Flask(__name__)

# Берём адрес базы данных из Переменной Окружения!
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    """Создаёт таблицу urls в базе данных при старте, если её ещё нет."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS urls (
                    id SERIAL PRIMARY KEY,
                    original_url TEXT NOT NULL,
                    short_code VARCHAR(10) UNIQUE NOT NULL,
                    clicks INTEGER DEFAULT 0
                );
            """)
            conn.commit()

HTML_PAGE = """
<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <title>DevOps URL Shortener</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 750px; margin: 40px auto; padding: 0 20px; background: #f4f6f9; }
        .card { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        input[type=text] { width: 72%; padding: 10px; font-size: 16px; border: 1px solid #ccc; border-radius: 4px; }
        button { padding: 10px 18px; font-size: 16px; background: #0066ff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        table { width: 100%; border-collapse: collapse; margin-top: 25px; }
        th, td { border-bottom: 1px solid #eee; padding: 10px; text-align: left; }
        .host { margin-top: 20px; color: #666; font-size: 13px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🔗 DevOps URL Shortener</h2>
        <form method="POST" action="/">
            <input type="text" name="url" placeholder="Вставьте длинную ссылку (например, https://github.com)" required>
            <button type="submit">Сократить</button>
        </form>
        <table>
            <tr><th>Короткая ссылка</th><th>Оригинал</th><th>Клики</th></tr>
            {% for row in urls %}
            <tr>
                <td><a href="/{{ row[2] }}" target="_blank">/{{ row[2] }}</a></td>
                <td>{{ row[1][:50] }}</td>
                <td><b>{{ row[3] }}</b></td>
            </tr>
            {% endfor %}
        </table>
        <div class="host">🖥 Ответ от контейнера (hostname): <b>{{ hostname }}</b></div>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    init_db()
    if request.method == "POST":
        original_url = request.form.get("url", "").strip()
        if not original_url.startswith(("http://", "https://")):
            original_url = "https://" + original_url
        short_code = "".join(random.choices(string.ascii_letters + string.digits, k=5))
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO urls (original_url, short_code) VALUES (%s, %s)", (original_url, short_code))
                conn.commit()
        return redirect("/")

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, original_url, short_code, clicks FROM urls ORDER BY id DESC;")
            urls = cur.fetchall()
    return render_template_string(HTML_PAGE, urls=urls, hostname=socket.gethostname())

@app.route("/health")
def health():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
        return jsonify({"status": "ok", "database": "connected", "hostname": socket.gethostname()}), 200
    except Exception as e:
        return jsonify({"status": "error", "details": str(e)}), 500

@app.route("/<short_code>")
def redirect_to_url(short_code):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE urls SET clicks = clicks + 1 WHERE short_code = %s RETURNING original_url;", (short_code,))
            result = cur.fetchone()
            conn.commit()
    if result:
        return redirect(result[0], code=302)
    return "Ссылка не найдена (404)", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


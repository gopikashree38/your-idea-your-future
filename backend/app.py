import sqlite3
import os
from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
from functools import wraps
from datetime import datetime

app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.secret_key = 'your-secret-key-change-this-in-production'

# Database configuration
DATABASE = 'feedback.db'
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'  # Change this in production!


def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with required tables."""
    if not os.path.exists(DATABASE):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                rating INTEGER NOT NULL,
                comments TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()


def login_required(f):
    """Decorator to check if admin is logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Serve the main feedback portal page."""
    with open('../frontend/index.html', 'r', encoding='utf-8') as f:
        return f.read()


@app.route("/api/feedback", methods=["POST"])
def submit_feedback():
    """Public endpoint: submit feedback. Does not expose any data."""
    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    rating = data.get("rating")
    comments = (data.get("comments") or "").strip()

    errors = []

    if not name:
        errors.append("Name is required.")
    if not email:
        errors.append("Email is required.")
    elif "@" not in email or "." not in email:
        errors.append("Email appears invalid.")

    try:
        rating_int = int(rating)
        if rating_int < 1 or rating_int > 5:
            errors.append("Rating must be between 1 and 5.")
    except (TypeError, ValueError):
        errors.append("Rating must be a number between 1 and 5.")

    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    ua = request.headers.get("User-Agent", "")

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO feedback (name, email, rating, comments)
        VALUES (?, ?, ?, ?)
        """,
        (name, email, rating_int, comments),
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Thank you for your feedback!"})


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Admin login page + handler."""
    error = None

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            error = "Invalid username or password."

    login_html = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Admin Login - Secure Feedback Portal</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #0f172a;
      color: #e5e7eb;
      margin: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
    }
    .card {
      background: #020617;
      border-radius: 16px;
      padding: 32px;
      max-width: 400px;
      width: 90%;
      box-shadow: 0 20px 40px rgba(0,0,0,0.5);
      border: 1px solid #1f2937;
    }
    h1 {
      margin-top: 0;
      font-size: 1.5rem;
      text-align: center;
      margin-bottom: 1.5rem;
      color: #f9fafb;
    }
    label {
      display: block;
      margin-bottom: 0.5rem;
      font-size: 0.9rem;
      color: #e5e7eb;
    }
    input[type=text],
    input[type=password] {
      width: 100%;
      padding: 0.6rem 0.75rem;
      border-radius: 999px;
      border: 1px solid #4b5563;
      background: #020617;
      color: #e5e7eb;
      outline: none;
      font-size: 0.9rem;
    }
    input[type=text]:focus,
    input[type=password]:focus {
      border-color: #38bdf8;
      box-shadow: 0 0 0 1px #38bdf8;
    }
    .button {
      margin-top: 1.25rem;
      width: 100%;
      padding: 0.7rem 1rem;
      border-radius: 999px;
      border: none;
      font-weight: 600;
      font-size: 0.95rem;
      background: linear-gradient(135deg, #38bdf8, #22c55e);
      color: #020617;
      cursor: pointer;
      transition: transform 0.15s ease, box-shadow 0.15s ease, opacity 0.15s ease;
    }
    .button:hover {
      transform: translateY(-1px);
      box-shadow: 0 10px 24px rgba(0,0,0,0.45);
      opacity: 0.95;
    }
    .button:active {
      transform: translateY(0);
      box-shadow: none;
    }
    .error {
      background: rgba(248,113,113,0.12);
      border: 1px solid rgba(248,113,113,0.6);
      color: #fecaca;
      padding: 0.6rem 0.75rem;
      border-radius: 0.75rem;
      font-size: 0.85rem;
      margin-bottom: 1rem;
    }
    .subtitle {
      text-align: center;
      font-size: 0.85rem;
      color: #9ca3af;
      margin-top: 0.25rem;
      margin-bottom: 1.5rem;
    }
    .back-link {
      text-align: center;
      margin-top: 1rem;
      font-size: 0.85rem;
    }
    .back-link a {
      color: #38bdf8;
      text-decoration: none;
    }
    .back-link a:hover {
      text-decoration: underline;
    }
  </style>
</head>
<body>
  <div class="card">
    <h1>Admin Login</h1>
    <p class="subtitle">Secure access to feedback dashboard</p>
    {% if error %}
      <div class="error">{{ error }}</div>
    {% endif %}
    <form method="post" autocomplete="off">
      <label for="username">Username</label>
      <input id="username" name="username" type="text" required>

      <label for="password" style="margin-top:0.85rem;">Password</label>
      <input id="password" name="password" type="password" required>

      <button class="button" type="submit">Sign in</button>
    </form>
    <div class="back-link">
      <a href="{{ url_for('index') }}">← Back to portal</a>
    </div>
  </div>
</body>
</html>
    """
    return render_template_string(login_html, error=error)


def is_admin():
    return bool(session.get("admin_logged_in"))


@app.route("/admin/dashboard")
def admin_dashboard():
    """Admin-only dashboard showing all feedback entries."""
    if 'admin_logged_in' not in session:
        return redirect(url_for("admin_login"))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM feedback ORDER BY submitted_at DESC')
    feedbacks = cursor.fetchall()
    conn.close()

    dashboard_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - Secure Feedback Portal</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }

        nav {
            background-color: #2c3e50;
            color: white;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        nav .title {
            font-size: 1.5rem;
            font-weight: 700;
        }

        .logout-btn {
            background-color: #e74c3c;
            color: white;
            padding: 0.7rem 1.5rem;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            transition: background-color 0.3s ease;
        }

        .logout-btn:hover {
            background-color: #c0392b;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }

        .dashboard-header {
            background-color: rgba(255, 255, 255, 0.9);
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }

        .dashboard-header h1 {
            color: #2c3e50;
            margin-bottom: 0.5rem;
        }

        .dashboard-header p {
            color: #7f8c8d;
        }

        .table-container {
            background-color: rgba(255, 255, 255, 0.9);
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        thead {
            background-color: #34495e;
            color: white;
        }

        th {
            padding: 1rem;
            text-align: left;
            font-weight: 600;
        }

        td {
            padding: 1rem;
            border-bottom: 1px solid #ecf0f1;
        }

        tr:hover {
            background-color: #f8f9fa;
        }

        .rating {
            display: inline-block;
            background-color: #3498db;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-weight: 600;
        }

        .no-feedback {
            text-align: center;
            color: #7f8c8d;
            padding: 2rem;
            font-style: italic;
        }

        .timestamp {
            color: #95a5a6;
            font-size: 0.9rem;
        }

        @media (max-width: 768px) {
            nav {
                flex-direction: column;
                gap: 1rem;
            }

            .table-container {
                overflow-x: auto;
            }

            table {
                font-size: 0.9rem;
            }

            th, td {
                padding: 0.75rem 0.5rem;
            }
        }
    </style>
</head>
<body>
    <nav>
        <div class="title">Admin Dashboard</div>
        <form action="{{ url_for('admin_logout') }}" method="post" style="margin:0;">
            <button class="logout-btn" type="submit">Logout</button>
        </form>
    </nav>

    <div class="container">
        <div class="dashboard-header">
            <h1>Feedback Management</h1>
            <p>View and manage all submitted feedback entries below.</p>
        </div>

        <div class="table-container">
            {% if feedbacks %}
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Rating</th>
                        <th>Comments</th>
                        <th>Submitted At</th>
                    </tr>
                </thead>
                <tbody>
                    {% for feedback in feedbacks %}
                    <tr>
                        <td>{{ feedback['id'] }}</td>
                        <td>{{ feedback['name'] }}</td>
                        <td>{{ feedback['email'] }}</td>
                        <td><span class="rating">{{ feedback['rating'] }}/5</span></td>
                        <td>{{ feedback['comments'] if feedback['comments'] else 'N/A' }}</td>
                        <td><span class="timestamp">{{ feedback['submitted_at'] }}</span></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p class="no-feedback">No feedback entries yet.</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
    """
    return render_template_string(dashboard_html, feedbacks=feedbacks)


@app.route("/admin/logout", methods=["POST", "GET"])
def admin_logout():
    """End admin session."""
    session.clear()
    return redirect(url_for("admin_login"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)

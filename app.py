"""
ACEest Fitness & Gym – Flask REST API
Converted from Aceestver-3.2.4 (Tkinter) to Flask for DevOps deployment.
Course: CSIZG514/SEZG514/SEUSZG514 – S2-25, BITS Pilani
"""

import os
import sqlite3
from datetime import datetime
from flask import Flask, jsonify, request, session, g

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "aceest-secret-2024")

DB_NAME = os.environ.get("DB_NAME", "aceest_fitness.db")

# ---------- PROGRAMS (from Aceestver-1.1, 2.x, 3.x) ----------
PROGRAMS = {
    "Fat Loss": {
        "factor": 22,
        "workout": "Mon: Back Squat 5x5 + Core | Tue: EMOM 20min Assault Bike | "
                   "Wed: Bench Press + 21-15-9 | Thu: Deadlift + Box Jumps | Fri: Zone 2 Cardio 30min",
        "diet": "Breakfast: Egg Whites + Oats | Lunch: Grilled Chicken + Brown Rice | "
                "Dinner: Fish Curry + Millet Roti | Target: ~2000 kcal",
        "color": "#e74c3c"
    },
    "Muscle Gain": {
        "factor": 35,
        "workout": "Mon: Squat 5x5 | Tue: Bench 5x5 | Wed: Deadlift 4x6 | "
                   "Thu: Front Squat 4x8 | Fri: Incline Press 4x10 | Sat: Barbell Rows 4x10",
        "diet": "Breakfast: Eggs + PB Oats | Lunch: Chicken Biryani | "
                "Dinner: Mutton Curry + Jeera Rice | Target: ~3200 kcal",
        "color": "#2ecc71"
    },
    "Beginner": {
        "factor": 26,
        "workout": "Full Body Circuit: Air Squats, Ring Rows, Push-ups | Focus: Technique & Consistency",
        "diet": "Balanced Tamil Meals: Idli-Sambar, Rice-Dal, Chapati | Protein Target: 120g/day",
        "color": "#3498db"
    }
}


# ---------- DATABASE ----------
def get_db():
    """Get per-request database connection (stored on Flask g object)."""
    if "db" not in g:
        g.db = sqlite3.connect(DB_NAME)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create all tables and seed default admin user."""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            age INTEGER,
            height REAL,
            weight REAL,
            program TEXT,
            calories INTEGER,
            target_weight REAL,
            target_adherence INTEGER,
            membership_status TEXT DEFAULT 'Active',
            membership_end TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            week TEXT,
            adherence INTEGER
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            date TEXT,
            workout_type TEXT,
            duration_min INTEGER,
            notes TEXT
        )
    """)

    # Seed default admin (from Aceestver-3.2.4 login screen)
    cur.execute(
        "INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
        ("admin", "admin123", "Admin")
    )

    conn.commit()
    conn.close()


# ---------- HELPERS ----------
def calculate_calories(weight, program_name):
    """Calculate daily calories: weight * program factor (from Aceestver-2.0.1)."""
    program = PROGRAMS.get(program_name)
    if not program or not weight:
        return 0
    return int(float(weight) * program["factor"])


def validate_client_data(data):
    """Validate required client fields."""
    if not data.get("name"):
        return False, "Client name is required"
    if not data.get("program"):
        return False, "Program is required"
    if data.get("program") and data["program"] not in PROGRAMS:
        return False, f"Invalid program. Choose from: {', '.join(PROGRAMS.keys())}"
    if data.get("adherence") is not None:
        try:
            val = int(data["adherence"])
            if val < 0 or val > 100:
                return False, "Adherence must be between 0 and 100"
        except (ValueError, TypeError):
            return False, "Adherence must be an integer"
    return True, ""


# ---------- ROUTES ----------

@app.route("/")
def index():
    """Landing page listing all API endpoints."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ACEest Fitness & Gym API</title>
        <style>
            body { font-family: Arial, sans-serif; background: #1a1a1a; color: #fff; padding: 40px; }
            h1 { color: #d4af37; }
            h2 { color: #d4af37; margin-top: 30px; }
            table { border-collapse: collapse; width: 100%; margin-top: 10px; }
            th { background: #d4af37; color: black; padding: 10px; text-align: left; }
            td { padding: 8px 10px; border-bottom: 1px solid #333; }
            code { background: #333; padding: 2px 6px; border-radius: 4px; color: #d4af37; }
            .badge { background: #333; padding: 2px 8px; border-radius: 10px; font-size: 12px; }
        </style>
    </head>
    <body>
        <h1>ACEest Fitness & Gym</h1>
        <p>Flask REST API — DevOps Assignment | BITS Pilani S2-25</p>
        <h2>Available Endpoints</h2>
        <table>
            <tr><th>Method</th><th>Endpoint</th><th>Description</th></tr>
            <tr><td>GET</td><td><code>/health</code></td><td>Health check</td></tr>
            <tr><td>POST</td><td><code>/api/login</code></td><td>Login</td></tr>
            <tr><td>POST</td><td><code>/api/logout</code></td><td>Logout</td></tr>
            <tr><td>GET</td><td><code>/api/clients</code></td><td>List all clients</td></tr>
            <tr><td>POST</td><td><code>/api/clients</code></td><td>Create client</td></tr>
            <tr><td>GET</td><td><code>/api/clients/&lt;name&gt;</code></td><td>Get client</td></tr>
            <tr><td>PUT</td><td><code>/api/clients/&lt;name&gt;</code></td><td>Update client</td></tr>
            <tr><td>DELETE</td><td><code>/api/clients/&lt;name&gt;</code></td><td>Delete client</td></tr>
            <tr><td>GET</td><td><code>/api/programs</code></td><td>List programs</td></tr>
            <tr><td>GET</td><td><code>/api/programs/&lt;name&gt;</code></td><td>Program detail</td></tr>
            <tr><td>GET</td><td><code>/api/clients/&lt;name&gt;/progress</code></td><td>Get progress</td></tr>
            <tr><td>POST</td><td><code>/api/clients/&lt;name&gt;/progress</code></td><td>Log weekly adherence</td></tr>
            <tr><td>GET</td><td><code>/api/clients/&lt;name&gt;/workouts</code></td><td>Get workouts</td></tr>
            <tr><td>POST</td><td><code>/api/clients/&lt;name&gt;/workouts</code></td><td>Log workout</td></tr>
            <tr><td>GET</td><td><code>/api/clients/&lt;name&gt;/membership</code></td><td>Check membership</td></tr>
        </table>
        <p style="margin-top:30px; color:#888;">Default login: admin / admin123</p>
    </body>
    </html>
    """
    return html


@app.route("/health")
def health():
    return jsonify({"status": "healthy", "app": "ACEest Fitness & Gym"}), 200


# ---------- AUTH ----------
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    db = get_db()
    row = db.execute(
        "SELECT role FROM users WHERE username=? AND password=?", (username, password)
    ).fetchone()

    if not row:
        return jsonify({"error": "Invalid credentials"}), 401

    session["user"] = username
    session["role"] = row["role"]
    return jsonify({"status": "ok", "user": username, "role": row["role"]}), 200


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"status": "logged out"}), 200


# ---------- CLIENTS ----------
@app.route("/api/clients", methods=["GET"])
def list_clients():
    db = get_db()
    rows = db.execute("SELECT * FROM clients ORDER BY name").fetchall()
    clients = [dict(r) for r in rows]
    return jsonify({"clients": clients, "count": len(clients)}), 200


@app.route("/api/clients", methods=["POST"])
def create_client():
    data = request.get_json() or {}
    valid, msg = validate_client_data(data)
    if not valid:
        return jsonify({"error": msg}), 400

    name = data["name"].strip()
    program = data["program"].strip()
    weight = data.get("weight", 0)
    calories = calculate_calories(weight, program)

    db = get_db()
    try:
        db.execute(
            """INSERT INTO clients
               (name, age, height, weight, program, calories, target_weight,
                target_adherence, membership_status, membership_end)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                name,
                data.get("age"),
                data.get("height"),
                weight,
                program,
                calories,
                data.get("target_weight"),
                data.get("target_adherence"),
                data.get("membership_status", "Active"),
                data.get("membership_end"),
            ),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": f"Client '{name}' already exists"}), 409

    return jsonify({"status": "created", "name": name, "calories": calories}), 201


@app.route("/api/clients/<string:name>", methods=["GET"])
def get_client(name):
    db = get_db()
    row = db.execute("SELECT * FROM clients WHERE name=?", (name,)).fetchone()
    if not row:
        return jsonify({"error": f"Client '{name}' not found"}), 404
    return jsonify(dict(row)), 200


@app.route("/api/clients/<string:name>", methods=["PUT"])
def update_client(name):
    db = get_db()
    row = db.execute("SELECT * FROM clients WHERE name=?", (name,)).fetchone()
    if not row:
        return jsonify({"error": f"Client '{name}' not found"}), 404

    data = request.get_json() or {}
    current = dict(row)

    program = data.get("program", current["program"])
    weight = data.get("weight", current["weight"])
    calories = calculate_calories(weight, program) if program and weight else current["calories"]

    db.execute(
        """UPDATE clients SET age=?, height=?, weight=?, program=?, calories=?,
           target_weight=?, target_adherence=?, membership_status=?, membership_end=?
           WHERE name=?""",
        (
            data.get("age", current["age"]),
            data.get("height", current["height"]),
            weight,
            program,
            calories,
            data.get("target_weight", current["target_weight"]),
            data.get("target_adherence", current["target_adherence"]),
            data.get("membership_status", current["membership_status"]),
            data.get("membership_end", current["membership_end"]),
            name,
        ),
    )
    db.commit()
    return jsonify({"status": "updated", "name": name, "calories": calories}), 200


@app.route("/api/clients/<string:name>", methods=["DELETE"])
def delete_client(name):
    db = get_db()
    row = db.execute("SELECT id FROM clients WHERE name=?", (name,)).fetchone()
    if not row:
        return jsonify({"error": f"Client '{name}' not found"}), 404

    db.execute("DELETE FROM clients WHERE name=?", (name,))
    db.execute("DELETE FROM progress WHERE client_name=?", (name,))
    db.execute("DELETE FROM workouts WHERE client_name=?", (name,))
    db.commit()
    return jsonify({"status": "deleted", "name": name}), 200


# ---------- PROGRAMS ----------
@app.route("/api/programs", methods=["GET"])
def list_programs():
    result = {k: {"factor": v["factor"], "diet": v["diet"], "workout": v["workout"]}
              for k, v in PROGRAMS.items()}
    return jsonify({"programs": result}), 200


@app.route("/api/programs/<string:name>", methods=["GET"])
def get_program(name):
    program = PROGRAMS.get(name)
    if not program:
        return jsonify({"error": f"Program '{name}' not found"}), 404
    return jsonify({"name": name, **program}), 200


# ---------- PROGRESS (from Aceestver-2.0.1 save_progress) ----------
@app.route("/api/clients/<string:name>/progress", methods=["GET"])
def get_progress(name):
    db = get_db()
    if not db.execute("SELECT id FROM clients WHERE name=?", (name,)).fetchone():
        return jsonify({"error": f"Client '{name}' not found"}), 404
    rows = db.execute(
        "SELECT week, adherence FROM progress WHERE client_name=? ORDER BY id",
        (name,)
    ).fetchall()
    return jsonify({"client": name, "progress": [dict(r) for r in rows]}), 200


@app.route("/api/clients/<string:name>/progress", methods=["POST"])
def log_progress(name):
    db = get_db()
    if not db.execute("SELECT id FROM clients WHERE name=?", (name,)).fetchone():
        return jsonify({"error": f"Client '{name}' not found"}), 404

    data = request.get_json() or {}
    try:
        adherence = int(data.get("adherence", 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Adherence must be an integer"}), 400

    if adherence < 0 or adherence > 100:
        return jsonify({"error": "Adherence must be between 0 and 100"}), 400

    week = data.get("week") or datetime.now().strftime("Week %U - %Y")
    db.execute(
        "INSERT INTO progress (client_name, week, adherence) VALUES (?, ?, ?)",
        (name, week, adherence)
    )
    db.commit()
    return jsonify({"status": "logged", "client": name, "week": week, "adherence": adherence}), 201


# ---------- WORKOUTS (from Aceestver-3.2.4 add_workout) ----------
@app.route("/api/clients/<string:name>/workouts", methods=["GET"])
def get_workouts(name):
    db = get_db()
    if not db.execute("SELECT id FROM clients WHERE name=?", (name,)).fetchone():
        return jsonify({"error": f"Client '{name}' not found"}), 404
    rows = db.execute(
        "SELECT date, workout_type, duration_min, notes FROM workouts WHERE client_name=? ORDER BY date DESC",
        (name,)
    ).fetchall()
    return jsonify({"client": name, "workouts": [dict(r) for r in rows]}), 200


@app.route("/api/clients/<string:name>/workouts", methods=["POST"])
def log_workout(name):
    db = get_db()
    if not db.execute("SELECT id FROM clients WHERE name=?", (name,)).fetchone():
        return jsonify({"error": f"Client '{name}' not found"}), 404

    data = request.get_json() or {}
    workout_date = data.get("date") or datetime.now().strftime("%Y-%m-%d")
    workout_type = data.get("workout_type", "General")
    duration = data.get("duration_min", 60)
    notes = data.get("notes", "")

    db.execute(
        "INSERT INTO workouts (client_name, date, workout_type, duration_min, notes) VALUES (?, ?, ?, ?, ?)",
        (name, workout_date, workout_type, duration, notes)
    )
    db.commit()
    return jsonify({"status": "logged", "client": name, "date": workout_date, "type": workout_type}), 201


# ---------- MEMBERSHIP (from Aceestver-3.2.4 check_membership) ----------
@app.route("/api/clients/<string:name>/membership", methods=["GET"])
def check_membership(name):
    db = get_db()
    row = db.execute(
        "SELECT membership_status, membership_end FROM clients WHERE name=?", (name,)
    ).fetchone()
    if not row:
        return jsonify({"error": f"Client '{name}' not found"}), 404
    return jsonify({
        "client": name,
        "membership_status": row["membership_status"],
        "membership_end": row["membership_end"]
    }), 200


# ---------- ENTRY POINT ----------
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)

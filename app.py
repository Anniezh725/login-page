from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import (
    LoginManager, UserMixin, login_user, login_required,
    logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-key-change-this-in-production"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///duty.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to view the duty board."


# ---------- Models ----------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
 
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(120), nullable=True)
    on_duty = db.Column(db.Boolean, default=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ---------- Routes ----------

@app.route("/")
def index():
    return redirect(url_for("dashboard"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "error")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    employees = Employee.query.order_by(Employee.name).all()
    on_duty_count = sum(1 for e in employees if e.on_duty)
    return render_template(
        "dashboard.html",
        employees=employees,
        on_duty_count=on_duty_count,
        total=len(employees),
    )


@app.route("/checkin/<int:employee_id>", methods=["POST"])
@login_required
def checkin(employee_id):
    employee = db.session.get(Employee, employee_id)
    if employee is None:
        flash("Employee not found.", "error")
        return redirect(url_for("dashboard"))

    employee.on_duty = not employee.on_duty
    employee.last_updated = datetime.utcnow()
    db.session.commit()
    return redirect(url_for("dashboard"))


# ---------- CLI helper: init + seed database ----------

@app.cli.command("init-db")
def init_db():
    """Create tables and seed demo data. Run with: flask --app app init-db"""
    db.create_all()

    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin")
        admin.set_password("admin123")
        db.session.add(admin)

    if Employee.query.count() == 0:
        demo_employees = [
            Employee(name="Alice Chen", role="Front Desk", on_duty=True),
            Employee(name="Bob Lee", role="Security", on_duty=False),
            Employee(name="Chris Nair", role="Manager", on_duty=True),
            Employee(name="David Baker", role="Maintenance", on_duty=False),
            Employee(name="Emma Rossi", role="Front Desk", on_duty=False),
        ]
        db.session.bulk_save_objects(demo_employees)

    db.session.commit()
    print("Database initialized with demo data.")
    print("Login with username: admin / password: admin123")


if __name__ == "__main__":
    app.run(debug=True)

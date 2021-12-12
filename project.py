from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder= 'templates')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.secret_key = "created_by_voronovich"
db = SQLAlchemy(app)

class users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(50), unique = True)
    psw = db.Column(db.String(500), nullable = True)

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    product = db.Column(db.String(500))
    adress = db.Column(db.String(500))
    phone_number = db.Column(db.String(500))
    user_id = db.Column(db.Integer)

@app.route("/")
def home():
    return render_template("home_page.html")

@app.route("/order", methods = ["POST", "GET"])
def order():
    if not ("id" in session):
        flash("You need to log in first", "info")
        return redirect(url_for("home"))
    if request.method == "POST":
        try:
            products = request.form["product"]
            o = Orders(product = products, adress = request.form["adress"],
                 phone_number = request.form["phone_number"], user_id = session["id"])
            db.session.add(o)
            db.session.flush()
            db.session.commit()
            flash(f"You have ordered {products}", "info")
            return redirect(url_for("home"))
        except:
            db.session.rollback()
    return render_template("order.html")


@app.route("/login", methods = ["POST", "GET"])
def login():
    if "id" in session:
        flash("You have already been logged in", "info")
        return redirect(url_for("home"))
    if request.method == "POST":
        try:
            found_user = users.query.filter_by(email = request.form['email']).first()
            if found_user:
                if check_password_hash(found_user.psw, request.form['psw']):
                    session["id"] = found_user.id
                    flash("You have been logged in", "info")
                    return redirect(url_for("home"))
                else:
                    flash("Wrong password", "info")
                    return render_template("login.html")
            else:
                hash = generate_password_hash(request.form['psw'])
                u = users(email = request.form['email'], psw = hash)
                db.session.add(u)
                db.session.flush()
                session["id"] = u.id
                db.session.commit()
                flash("You have been registered", "info")
                return redirect(url_for("home"))
        except:
            db.session.rollback()

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("id", None)
    flash("You have been logged out", "info")
    return redirect(url_for("home"))


if __name__ == "__main__":
    db.create_all() 
    app.run(debug = True)


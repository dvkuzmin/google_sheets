from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template

import database

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database.Settings.DB_URL

db = SQLAlchemy(app)


@app.route("/")
def index():
    orders = db.session.query(database.Order).order_by(database.Order.order_id.asc()).all()
    return render_template("index.html", orders=orders)


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

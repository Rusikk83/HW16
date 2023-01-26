from flask import Flask, request, render_template, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
import db_data
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    age = db.Column(db.Integer)
    email = db.Column(db.String(50))
    role = db.Column(db.String(50))
    phone = db.Column(db.String(50))

    oredr = relationship("Order")
    offer = relationship("Offer")


class Order(db.Model):
    __tablename__ = "order"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    description = db.Column(db.String(500))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String(100))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    # executor_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    executor_id = db.Column(db.Integer, db.ForeignKey("offer.executor_id"))




class Offer(db.Model):
    __tablename__ = "offer"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer)
    executor_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    order = relationship("Order")


with app.app_context():
    db.create_all()

    with db.session.begin():
        for el in db_data.users:
            user = User(id=el["id"],
                        first_name=el["first_name"],
                        last_name=el["last_name"],
                        age=el["age"],
                        email=el["email"],
                        role=el["role"],
                        phone=el["phone"])
            db.session.add(user)

    print(db.session.query(User).all())

    db.session.commit()

    with db.session.begin():
        for el in db_data.orders:
            order = Order(id=el["id"],
                          name=el["name"],
                          description=el["description"],
                          start_date=datetime.datetime.strptime(el["start_date"], '%m/%d/%Y').date(),
                          end_date=datetime.datetime.strptime(el["end_date"], '%m/%d/%Y').date(),
                          address=el["address"],
                          price=el["price"],
                          customer_id=el["customer_id"],
                          executor_id=el["executor_id"])
            db.session.add(order)

    print(db.session.query(Order).all())
    db.session.commit()


    with db.session.begin():
        for el in db_data.offers:
            offer = Offer(id=el["id"],
                          order_id=el["order_id"],
                          executor_id=el["executor_id"])
            db.session.add(offer)

    print(db.session.query(Offer).all())
    db.session.commit()



@app.route("/")
def page_index():
    return "Ok"

@app.errorhandler(404)
def error_404(error):
    return "Запрошенная страница не существует", 404


if __name__ == "__main__":
    app.run()
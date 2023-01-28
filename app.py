import json

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
import db_data
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
db = SQLAlchemy(app)
app.config['JSON_AS_ASCII'] = False


"""Создаем модель пользователя"""
class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    age = db.Column(db.Integer)
    email = db.Column(db.String(50))
    role = db.Column(db.String(50))
    phone = db.Column(db.String(50))

    orders = relationship("Order")
    offers = relationship("Offer")


"""Создаем модель заказа"""
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
    executor_id = db.Column(db.Integer)

    customer = relationship("User")


"""Создаем модель предложения"""
class Offer(db.Model):
    __tablename__ = "offer"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"))
    executor_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    order = relationship("Order")
    executor = relationship("User")


def order_post(order_dict):
    """Создает запись заказа в БД из объекта словарь"""
    with db.session.begin():
        order = Order(id=order_dict["id"],
                      name=order_dict["name"],
                      description=order_dict["description"],
                      start_date=datetime.datetime.strptime(order_dict["start_date"], '%m/%d/%Y').date(),
                      end_date=datetime.datetime.strptime(order_dict["end_date"], '%m/%d/%Y').date(),
                      address=order_dict["address"],
                      price=order_dict["price"],
                      customer_id=order_dict["customer_id"],
                      executor_id=order_dict["executor_id"])
        db.session.add(order)
        db.session.commit()


def user_post(user_dict):
    """Создает запись пользователя в БД из объекта словарь"""
    user = User(id=user_dict["id"],
                first_name=user_dict["first_name"],
                last_name=user_dict["last_name"],
                age=user_dict["age"],
                email=user_dict["email"],
                role=user_dict["role"],
                phone=user_dict["phone"])
    db.session.add(user)
    db.session.commit()


def offer_post(offer_dict):
    """Создает запись предложения в БД из объекта словарь"""
    offer = Offer(id=offer_dict["id"],
                  order_id=offer_dict["order_id"],
                  executor_id=offer_dict["executor_id"])
    db.session.add(offer)
    db.session.commit()


with app.app_context():
    db.create_all()

    for user_dict in db_data.users:  #заполняем таблицу пользователей из  db_data
        user_post(user_dict)

    for order_dict in db_data.orders:  #заполняем таблицу заказов из  db_data
        order_post(order_dict)

    for offer_dict in db_data.offers:  #заполняем таблицу предложений из  db_data
        offer_post(offer_dict)


"""Представление для возврата всех пользователей и добавления нового"""
@app.route("/users", methods=["POST", "GET"])
def page_users_all():
    if request.method == "GET":
        users = (db.session.query(User).all())  #получаем всех пользователей
        result = []
        for user in users:  #производим сериализацию пользователей
            user_dict = {c.name: str(getattr(user, c.name)) for c in user.__table__.columns}
            result.append(user_dict)

        return json.dumps(result, ensure_ascii=False)  #возвращаем данные всех пользователей

    if request.method == "POST":
        new_user = request.json  #получаем значения атрибуто нового пользователя из запроса
        user_post(new_user)  #записываем нового пользователя в БД
        return "Ok"


"""Представление для возврата всех предложений и добавления нового"""
@app.route("/offers", methods=["POST", "GET"])
def page_offers_all():
    if request.method == "GET":
        offers = (db.session.query(Offer).all())
        result = []
        for offer in offers:
            offer_dict = {c.name: str(getattr(offer, c.name)) for c in offer.__table__.columns}
            result.append(offer_dict)

        return json.dumps(result, ensure_ascii=False)

    if request.method == "POST":
        new_offer = request.json
        offer_post(new_offer)
        return "Ok"


"""Представление для возврата всех заказов и добавления нового"""
@app.route("/orders", methods=["POST", "GET"])
def page_order_all():
    if request.method == "GET":
        orders = (db.session.query(Order).all())
        result = []
        for order in orders:
            order_dict = {c.name: str(getattr(order, c.name)) for c in order.__table__.columns}
            result.append(order_dict)

        return json.dumps(result, ensure_ascii=False)

    if request.method == "POST":
        new_order = request.json
        order_post(new_order)

        return "Ok"


"""Представление для получения, изменения и удаления пользователя по ID"""
@app.route("/users/<int:id>", methods=["GET", "PUT", "DELETE"])
def page_users_id(id):
    user = User.query.get(id)  #получение пользователя по ID из БД
    if user is None:  #если запись по ID не найдена
        return "Пользователь не найден", 400

    if request.method == "GET":
        user_dict = {c.name: str(getattr(user, c.name)) for c in user.__table__.columns}  #сериализация пользователя
        return json.dumps(user_dict, ensure_ascii=False)  #возвращаем данные пользователя в виде JSON

    if request.method == "DELETE":
        db.session.delete(user)  #удаление пользователя
        db.session.commit()
        return "Ok"

    if request.method == "PUT":
        for k, v in request.json.items():  #присваиваем значение атрибутов экземпляру из JSON в запросе
            if isinstance(getattr(user, k), datetime.date):  #если поле типа дата, то преобразуем тип
                date_v = datetime.datetime.strptime(v, "%Y-%m-%d").date()  #преобразование строки в дату
                setattr(user, k, date_v)  #непосредственно присвоение значение атрибуту по имени
            else:
                setattr(user, k, v)  #непосредственно присвоение значение атрибуту по имени
            db.session.add(user)  #добавление пользователя
            db.session.commit()  #подтверждение транзакции
        return "Ok"


"""Представление для получения, изменения и удаления предложения по ID"""
@app.route("/offers/<int:id>", methods=["GET", "PUT", "DELETE"])
def page_offers_id(id):
    offer = Offer.query.get(id)
    if offer is None:
        return "Предложение не найдено", 400

    if request.method == "GET":
        offer_dict = {c.name: str(getattr(offer, c.name)) for c in offer.__table__.columns}
        return json.dumps(offer_dict, ensure_ascii=False)

    if request.method == "DELETE":
        db.session.delete(offer)
        db.session.commit()
        return "Ok"

    if request.method == "PUT":
        for k, v in request.json.items():
            if isinstance(getattr(offer, k), datetime.date):
                date_v = datetime.datetime.strptime(v, "%Y-%m-%d").date()
                setattr(offer, k, date_v)
            else:
                setattr(offer, k, v)
            db.session.add(offer)
            db.session.commit()
        return "Ok"


"""Представление для получения, изменения и удаления заказа по ID"""
@app.route("/orders/<int:id>", methods=["GET", "PUT", "DELETE"])
def page_order_id(id):
    order = Order.query.get(id)
    if order is None:
        return "Заказ не найден", 400

    if request.method == "GET":
        order_dict = {c.name: str(getattr(order, c.name)) for c in order.__table__.columns}
        return json.dumps(order_dict, ensure_ascii=False)

    if request.method == "DELETE":
        db.session.delete(order)
        db.session.commit()
        return "Ok"

    if request.method == "PUT":
        for k, v in request.json.items():
            if isinstance(getattr(order, k), datetime.date):
                date_v = datetime.datetime.strptime(v, "%Y-%m-%d").date()
                setattr(order, k, date_v)
            else:
                setattr(order, k, v)
            db.session.add(order)
            db.session.commit()
        return "Ok"


@app.errorhandler(404)
def error_404(error):
    return "Запрошенная страница не существует", 404


if __name__ == "__main__":
    app.run()

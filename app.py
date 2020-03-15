from flask import Flask, render_template, request
import random
import json
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField
from wtforms.validators import InputRequired
from flask import abort

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///week4.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

day_dict = {'mon': 'Понедельник', 'tue': 'Вторник', 'wed': 'Среда', 'thu': 'Четверг', 'fri': 'Пятница',
            'sat': 'Суббота', 'sun': 'Воскресенье'}
goals = {"travel": "Для путешествий", "study": "Для учебы", "work": "Для работы", "relocate": "Для переезда"}

time_dict = {"1": "1-2 часа в неделю", "3": "3-5 часов в неделю", "5": "5-7 часов в неделю", "7": "7-10 часов в неделю"}


# Формы
class BookingForm(FlaskForm):
    name = StringField('Имя пользователя', [InputRequired()])
    phone = StringField('Телефон пользователя', [InputRequired()])


class RequestForm(FlaskForm):
    name = StringField('Имя пользователя', [InputRequired()])
    phone = StringField('Телефон пользователя', [InputRequired()])
    goal = RadioField('goal', choices=[('travel', 'Для путешествий'), ('study', 'Для учебы'), ('work', 'Для работы'), ('relocate', 'Для переезда')], default='travel')
    time = RadioField('time', choices=[('1', '1-2 часа в неделю'), ('3', '3-5 часов в неделю'), ('5', '5-7 часов в неделю'),
                                        ('7', '7-10 часов в неделю')], default='1')


# Модели
class Teacher(db.Model):
    __tablename__ = 'teachers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    about = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    picture = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    goals = db.Column(db.String, nullable=False)
    free = db.Column(db.String, nullable=False)
    bookings = db.relationship("Booking", back_populates="teacher")


class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String, nullable=False)
    clientName = db.Column(db.String, nullable=False)
    clientPhone = db.Column(db.String, nullable=False)

    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"), nullable=False)
    teacher = db.relationship("Teacher", back_populates="bookings")


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    clientName = db.Column(db.String, nullable=False)
    clientPhone = db.Column(db.String, nullable=False)
    goal = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)


@app.route('/')
def index_r():
    teach_list = db.session.query(Teacher).all()
    random_teachers = random.sample(teach_list, 6)
    goals_dict = goals

    return render_template('index.html', teachers=random_teachers, goals_data=goals_dict)


@app.route('/goals/<goal>/')
def goal_r(goal):
    clear_teach = []
    teach_list = db.session.query(Teacher).all()
    for item in teach_list:
        teacher_goals = json.loads(item.goals)
        if goal in teacher_goals:
            clear_teach.append(item)
    return render_template('goal.html', name=goals[goal].lower(), teachers=clear_teach)
    # return render_template('goal.html', name=goals[goal].lower(), teachers=clear_teach)


@app.route('/profiles/<id_teacher>/')
def teach_r(id_teacher):
    teach = db.session.query(Teacher).filter(Teacher.id == int(id_teacher)).first()
    if teach == None:
            abort(404)

    free = json.loads(teach.free)

    teach.free = free
    teach.goals = json.loads(teach.goals)
    return render_template('profile.html', id_teach=id_teacher, data_teach=teach,
                           data_goals=goals, days=day_dict)


# @app.route('/booking_old/<id_teacher>/<b_day>/<b_time>/')
# def booking_r(id_teacher, b_day, b_time):
#
#     teacher = db.session.query(Teacher).filter(Teacher.id == int(id_teacher)).first()
#
#     return render_template('booking.html', b_day=b_day, b_time=int(b_time), data_teach=teacher, days=day_dict)


# @app.route('/booking_done/', methods=['GET'])
# def booking_parse_request():
#     answer_dict = {'clientPhone': request.args.get('clientPhone'), 'clientWeekday': request.args.get('clientWeekday'),
#                    'clientTime': request.args.get('clientTime'), 'clientName': request.args.get('clientName'),
#                    'clientTeacher': request.args.get('clientTeacher')}
#
#     with open("booking.json", "w") as f:
#         json.dump(answer_dict, f)
#
#     return render_template('booking_done.html', data_dict=answer_dict, days=day_dict)


@app.route('/request_done/', methods=['POST'])
def request_parse_request():
    answer_dict = {"goal": request.form["goal"], "time": request.form["time"], "clientName": request.form["clientName"],
                   "clientPhone": request.form["clientPhone"]}

    with open("request.json", "w") as f:
        json.dump(answer_dict, f)

    return render_template('request_done.html', data_dict=answer_dict, days=day_dict, goals_data=data.goals)


@app.route('/upgrade/')
def generate_data():
    # t = []
    for item in data.teachers:
        name = item["name"]
        about = item["about"]
        rating = item["rating"]
        picture = item["picture"]
        price = item["price"]
        goals = json.dumps(item["goals"])
        free = json.dumps(item["free"])
        # t.append(Teacher(name, about, rating, picture, price, goals, free))
        teacher = Teacher(name=name, about=about, rating=rating, picture=picture, price=price, goals=goals, free=free)
        db.session.add(teacher)
    # db.session.add_all(t)
    db.session.commit()

    return "OK"


@app.route('/booking/<id_teacher>/<b_day>/<b_time>/', methods=['GET', 'POST'])
def bookingform(id_teacher, b_day, b_time):
    form = BookingForm()

    # Если данные были отправлены
    if request.method == "POST":

        # получаем данные
        name = form.name.data
        phone = form.phone.data

        # сохраняем в базу
        booking = Booking()
        booking.teacher_id = id_teacher
        booking.clientName = name
        booking.clientPhone = phone
        booking.time = '{:02}:{:02}'.format(int(b_time), 0)

        db.session.add(booking)
        db.session.commit()

        # выводим данные
        return render_template("booking_done.html", name=name, phone=phone, weekday=b_day, time='{:02}:{:02}'.format(int(b_time), 0), days=day_dict)

    # Если данные еще НЕ были отправлены
    else:
        teacher = db.session.query(Teacher).filter(Teacher.id == int(id_teacher)).first()
        # выводим форму
        return render_template('bookingWTF.html', form=form, b_day=b_day, b_time=int(b_time), data_teach=teacher,
                               days=day_dict)


@app.route('/request/', methods=['GET', 'POST'])
def req_r():
    form = RequestForm()

    if request.method == "POST":

        name = form.name.data
        phone = form.phone.data
        goal = form.goal.data
        time = form.time.data

        answer_dict = {"goal": goal, "time": time_dict[time],
                       "clientName": name,
                       "clientPhone": phone}

        # сохраняем в базу
        order = Order()

        order.clientName = name
        order.clientPhone = phone
        order.goal = goal
        order.time = time

        db.session.add(order)
        db.session.commit()

        return render_template("request_done.html", data_dict=answer_dict, days=day_dict, goals_data=goals)
    else:
        return render_template('requestWTF.html', form=form)


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")

if __name__ == '__main__':
    app.secret_key = 'ggggggggg'
    app.run()

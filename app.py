import json
import random
import os

from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField
from wtforms.validators import InputRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.dialects.postgresql import JSON


app = Flask(__name__)
app.secret_key = "randomstring"

app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)
migrate = Migrate(app, db)


#Модель Дни недели
class Day(db.Model):
    __tablename__ = 'day'
    day_id = db.Column(db.Integer, primary_key=True)
    day_key_en = db.Column(db.String, nullable=False)
    day_value_ru = db.Column(db.String, nullable=False)


# Модель Ассоциативная таблица Преподаватели-Цели
teachers_goals_association = db.Table('teachers_goals', db.metadata,
    db.Column('teacher_id', db.Integer, db.ForeignKey('teachers.id')),
    db.Column('goal_id', db.Integer, db.ForeignKey('goals.id')))


# Модель Цели
class Goal(db.Model):
    __tablename__ = 'goals'
    id = db.Column(db.Integer, primary_key=True)
    goal_key_en = db.Column(db.String, nullable=False)
    goal_value_ru = db.Column(db.String, nullable=False)
    teachers = db.relationship("Teacher", secondary=teachers_goals_association, back_populates="goals")


#Модель Бронирование
class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)
    day = db.Column(db.String, nullable=False)
    teach_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    teach = db.relationship('Teacher', back_populates='bookings')


# Модель Преподаватель
class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    # id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String, nullable=False)
    about = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    picture = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    goals = db.relationship("Goal", secondary=teachers_goals_association, back_populates="teachers")
    free = db.Column(JSON)
    bookings = db.relationship('Booking', back_populates='teach')


# Модель Заявка
class Request(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, primary_key=True)
    goal = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)


class UserForm(FlaskForm):
    name = StringField('Вас зовут', [InputRequired()])
    phone = StringField('Ваш телефон', [InputRequired()])
    clientDay = StringField()
    clientTime = StringField()
    clientTeacher = StringField()


class MyRequest(FlaskForm):
    goals = Goal.query.all()
    goals_list = []
    for goal in goals:
        goals_list.append((goal.goal_key_en, goal.goal_value_ru))
    goal_request = RadioField ("Какая цель занятий?", choices = goals_list, default="travel")
    time_request = RadioField("Сколько времени есть?",
                              choices = [("1-2 часа в неделю", "1-2 часа в неделю"),
                                        ("3-5 часов в неделю","3-5 часов в неделю"),
                                        ("5-7 часов в неделю","5-7 часов в неделю"),
                                        ("7-10 часов в неделю","7-10 часов в неделю")],
                              default="5-7 часов в неделю")
    name_request = StringField("Вас зовут", [InputRequired()])
    phone_request = StringField("Ваш телефон", [InputRequired()])


@app.route('/')
def render_index():
    teachers = Teacher.query.all()
    goals = Goal.query.all()
    list_index = list(range(0, len(teachers)))
    index = random.sample(list_index, 7)
    return render_template("index.html",
                           teachers = teachers,
                           goals = goals,
                           index = index
                           )


@app.route('/goals/<goal>/')
def render_goal(goal):
    if goal == 'allteachers':
        teachers = Teacher.query.order_by(Teacher.rating.desc()).all()
        goals = Goal.query.all()
    else:
        goals = db.session.query(Goal).filter(Goal.goal_key_en == goal).first()
        teachers = db.session.query(Teacher).join(teachers_goals_association, Goal)\
            .filter(Goal.goal_key_en == goal).order_by(Teacher.rating.desc()).all()

    return render_template("goal.html",
                           teachers = teachers,
                           goals = goals
                               )


@app.route('/profile/<int:id>/')
def render_profile(id):
    teachers = db.session.query(Teacher).get_or_404(id)
    teachers.free = json.loads(teachers.free)
    goals = teachers.goals
    days = Day.query.all()
    return render_template("profile.html",
                           teachers = teachers,
                           goals = goals,
                           id = id,
                           days = days
                           )


@app.route('/booking/<int:id>/<day>/<time>/', methods=["GET","POST"])
def render_booking(id, day, time):
    teachers = Teacher.query.filter(Teacher.id == id).first()
    days = Day.query.filter(Day.day_value_ru == day).first()
    form = UserForm()
    if request.method == "POST":
        name = form.name.data
        phone = form.phone.data
        clientDay = days.day_value_ru
        clientTime = time
        clientTeacher = id
        client = Booking(name = name, phone = phone, time = time, day = days.day_value_ru, teach_id = id )
        db.session.add(client)
        db.session.commit()
        free_timeframe = json.loads(teachers.free)
        free_timeframe[days.day_key_en][time] = False
        teachers.free = json.dumps(free_timeframe)
        db.session.add(teachers)
        db.session.commit()
        return render_template("booking_done.html",
                           teachers = teachers,
                           id = id,
                           day = day,
                           time = time,
                           clientDay = clientDay,
                           clientTime = clientTime,
                           clientTeacher = clientTeacher,
                           name = name,
                           phone = phone,
                           form = form
                           )
    else:
        teachers = Teacher.query.filter(Teacher.id == id).first()
        name = form.name.data
        phone = form.phone.data
        clientDay = form.clientDay.data
        clientTime = form.clientTime.data
        clientTeacher = form.clientTeacher.data
        return render_template("booking.html",
                           teachers = teachers,
                           id = id,
                           day = day,
                           time = time,
                           name = name,
                           phone = phone,
                           clientDay = clientDay,
                           clientTime = clientTime,
                           clientTeacher = clientTeacher,
                           form = form
                           )


@app.route('/request/', methods=["GET","POST"])
def render_request():
    goals = Goal.query.all()
    form = MyRequest()

    if request.method == "POST":
        goal_request = form.goal_request.data
        time_request = form.time_request.data
        name_request = form.name_request.data
        phone_request = form.phone_request.data
        req = Request(goal = goal_request, time = time_request, name = name_request, phone = phone_request)
        db.session.add(req)
        db.session.commit()
        return render_template("request_done.html",
                               goal_request = goal_request,
                               time_request = time_request,
                               name_request = name_request,
                               phone_request = phone_request,
                               form = form,
                               goals = goals
                               )
    else:
        return render_template("request.html",
                               form = form
                               )


# if __name__ == '__main__':


    # app.run(debug=True)
import os

from flask import Flask, redirect, render_template, jsonify, request
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from data import db_session
from data.student import Student
from data.room import Room
from data.hostel import Hostel
from data.tag import Tag
from data.studentsANDtags import StudentAndTag
from form.loginform import LoginForm
from form.registrationform import RegistrationForm
from flasgger import Swagger
from api.resources import Application_request, RoomItemResource, RoomListResource, StudentItemResource, StudentListResource, HostelItemResource, HostelListResource, ReportResource
from api.routes import initialize_routes
from flask_restful import Api
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pfybvfqntcmcgjhnfvvfkmxbrbbltdjxrb'
login_manager = LoginManager()
login_manager.init_app(app)

swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "API документация",
        "description": "Документация для всех доступных API",
        "version": "1.0"
    },
    "host": "prod-team-18-lkt02gu5.hack.prodcontest.ru",
    "basePath": "/",
    "schemes": [
        "http"
    ],
    "tags": [
        {
            "name": "Application Requests",
            "description": "Операции с заявками"
        },
        {
            "name": "Students",
            "description": "Операции со студентами"
        },
        {
            "name": "Rooms",
            "description": "Операции с комнатами"
        },
        {
            "name": "Hostels",
            "description": "Операции с общежитиями"
        }
    ]
})

# Инициализация Flask-RESTful
api = Api(app)

# Инициализация маршрутов API
initialize_routes(api)

# !!! ДОБАВЬ ЭТУ СТРОКУ ДЛЯ ВКЛЮЧЕНИЯ CORS !!!
# Разрешить CORS для всех маршрутов и всех источников
# Это может быть небезопасно, если у вас есть чувствительные данные или вы хотите ограничить доступ к API.
# Лучше использовать более строгие настройки CORS в продакшене.
# Строка ниже решает проблему "TypeError: NetworkError when attempting to fetch resource." в Swagger UI.
CORS(app)
# Если тебе нужно ограничить разрешенные источники, можно сделать так:
# CORS(app, resources={r"/api/*": {"origins": "http://localhost:твоего_порта_с_swagger"}})
# где "твоего_порта_с_swagger" - это порт, на котором открывается интерфейс Swagger UI в браузере.

def init_db():
    # Используйте относительный путь от корня проекта
    db_path = os.path.join(os.path.dirname(__file__), "db/database.db")
    print(f"Initializing database at: {db_path}")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    db_session.global_init(db_path)


def main():
    init_db()
    app.run()


# загрузка пользователя, прошедшего логин
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(Student).get(user_id)


# основная страница
@app.route('/')
def main_page():
    return render_template("basepage.html")


# страница пользователя
@app.route('/me')
def myself():
    if not current_user.is_authenticated:
        return redirect('/login')
    return render_template('aboutuser.html', item=current_user)


# страница общежитий
@app.route('/hostels')
def hostel():
    return render_template('finding.html')


@app.route('/rooms')
def room():
    return render_template('application.html')


# регистрация
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        return redirect('/')
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.password.data != form.repeat_password.data:
            return render_template('registration.html', form=form, message='Пароли не совпадают')
        db_sess = db_session.create_session()
        if db_sess.query(Student).filter(Student.login == form.email.data).first():
            return render_template('registration.html', form=form,
                                   message='Пользователь с такой электронной почтой уже существует')
        student = Student(
            login=form.email.data,
            name=form.name.data,
            surname=form.surname.data,
            sex=1
        )

        student.set_password(form.password.data)
        db_sess.add(student)
        db_sess.commit()
        db_sess.close()
        return redirect('/login')
    return render_template('registration.html', form=form)


# страница логина
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        student = db_sess.query(Student).filter(Student.login == form.login.data).first()
        if student and student.check_password(form.password.data):
            login_user(student, remember=form.remember_me.data)
            db_sess.close()
            return redirect("/")
        db_sess.close()
        return render_template('login.html', form=form, message='Неверно введён логин или пароль')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/applications')
def applications():
    return render_template('applications.html', user=current_user)


@app.route('/admin')
def admin():
    return render_template('admin.html', user=current_user)


@app.route('/admin_profile')
def admin_profile():
    return render_template('admin_profile.html', user=current_user)

@app.route('/add', methods=['GET'])
def add():
    """
        Add room
        ---
        parameters:
          - name: id
            in: query
            type: integer
            required: true
          - name: hostel_id
            in: query
            type: integer
            required: true
          - name: square
            in: query
            type: integer
            required: true
          - name: max_cnt_student
            in: query
            type: integer
            required: true
          - name: cur_cnt_student
            in: query
            type: integer
            required: true
          - name: floor
            in: query
            type: integer
            required: true
          - name: sex
            in: query
            type: boolean
            required: true
          - name: side
            in: query
            type: string
            required: true
        responses:
          200:
            description: -_-
        """
    db_sess = db_session.create_session()
    room = Room(
        id=int(request.args.get('id')),
        hostel_id=int(request.args.get('hostel_id')),
        square=float(request.args.get('square')),
        max_cnt_student=int(request.args.get('max_cnt_student')),
        cur_cnt_student=int(request.args.get('cur_cnt_student')),
        floor=int(request.args.get('floor')),
        sex=bool(request.args.get('sex')),
        side=str(request.args.get('side'))
    )
    db_sess.add(room)
    db_sess.commit()
    db_sess.close()
    return jsonify({'result': 'fine'})


if __name__ == "__main__":
    main()

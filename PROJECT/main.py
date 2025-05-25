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
from functools import wraps
from flask import abort
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
from data.help_requests import HelpRequests

load_dotenv('config.env')  # загружаем переменные из .env
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
login_manager = LoginManager()
login_manager.init_app(app)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.admin:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function


@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html', 
                        error="Доступ запрещен. Необходимы права администратора."), 403


    # Добавьте эту строку перед инициализацией Swagger
# app.config['SWAGGER_URL'] = '/apidocs' # URL для Swagger UI

swagger = Swagger(app, template={
        "swagger": "2.0",
        "info": {
            "title": "API документация",
            "description": "Документация д  ля всех доступных API",
            "version": "1.0"
        },
        "consumes": [
        "application/json"
        ],
        # "host": f"",
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

def init_db():
    # Используйте относительный путь от корня проекта
    db_path = os.path.join(os.path.dirname(__file__), "db/database.db")
    print(f"Initializing database at: {db_path}")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    db_session.global_init(db_path)


def main():
    init_db()
    app.run(host="0.0.0.0", port=80)
    # server_base_url = request.url_root
    # if not server_base_url.endswith('/'):
    #     server_base_url += '/'



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
    db_sess = db_session.create_session()
    server_base_url = request.url_root
    if not server_base_url.endswith('/'):
        server_base_url += '/'
    if not current_user.is_authenticated:
        return redirect('/login')
    try:
        student_applications = db_sess.query(Application_request)\
                                        .filter(Application_request.student_id == current_user.id)\
                                        .all()
        applications_data = []
        for req in student_applications:
            applications_data.append({
                'id': req.id,
                'status': req.status,
                'date_entr': req.date_entr.strftime('%Y-%m-%d') if req.date_entr else 'Не указана',
                'date_exit': req.date_exit.strftime('%Y-%m-%d') if req.date_exit else 'Не указана',
                'room_id': req.room_id,
                'student_id': req.student_id,
                'comment': req.comment
            })

        return render_template('aboutuser.html', item=current_user, server_url=server_base_url, applications=applications_data)
    except Exception as e:
            # Обработка ошибок при загрузке данных
            print(f"Ошибка при загрузке профиля студента с ID {current_user.id}: {e}")
            return render_template('error.html', message=f"Произошла ошибка при загрузке профиля студента: {e}"), 500
    finally:
        # Обязательно закрываем сессию базы данных
        db_sess.close()


# страница общежитий
@app.route('/hostels')
def hostel():
    return render_template('finding.html')


@app.route('/filter')
def room():
    return (render_template('application.html'))


@app.route('/rooms')
def test_rooms():
    session = db_session.create_session()

    min_square = request.args.get('min_square', type=int)
    max_square = request.args.get('max_square', type=int)
    max_students = request.args.get('max_students', type=int)
    sex_filter = request.args.get('sex', 'any')

    query = session.query(Room)

    if min_square:
        query = query.filter(Room.square >= min_square)
    if max_square:
        query = query.filter(Room.square <= max_square)
    if max_students:
        query = query.filter(Room.max_cnt_student == max_students)
    if sex_filter != 'any':
        query = query.filter(Room.sex == int(sex_filter))  # Исправлено здесь

    rooms = query.all()

    return render_template('filter.html',
                           rooms=rooms,
                           current_filters=request.args)


@app.route('/book_room/<int:id>', methods=['GET', 'POST'])
def book_room(id):
    db_sess = db_session.create_session()

    if not current_user.is_authenticated:
        return redirect('/login')

    # Получаем информацию о комнате
    room = db_sess.query(Room).get(id)
    if not room:
        abort(404)

    # Получаем информацию о студенте
    student = db_sess.query(Student).get(current_user.id)
    if not student:
        abort(403)

    # Формируем базовый URL сервера
    server_base_url = request.url_root.rstrip('/') + '/'

    return render_template('book_room.html',
                           room=room,
                           item=student,
                           room_id=room.id,
                           server_url=server_base_url)


@app.route('/about')
def about():
    return render_template('about.html')

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
            sex=1,
            admin=0,
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
@admin_required
def applications():
    server_base_url = request.url_root
    if not server_base_url.endswith('/'):
        server_base_url += '/'
    return render_template('applications.html', user=current_user, server_url=server_base_url)


@app.route('/admin')
@admin_required
def admin():
    return render_template('admin.html', user=current_user)


@app.route('/admin_profile')
@admin_required
def admin_profile():
    return render_template('admin_profile.html', user=current_user)


@admin_required
@app.route('/admin_support_reply', methods=['GET', 'POST'])
def admin_support_reply():
    db_sess = db_session.create_session()
    if request.method == 'POST':
        req_id = request.form.get('request_id')
        reply_text = request.form.get('reply_text')
        help_request = db_sess.query(HelpRequests).get(int(req_id))
        if help_request and help_request.status == 'open':
            help_request.reply = reply_text
            help_request.status = 'closed'
            db_sess.commit()
    # Получаем все открытые запросы
    open_requests = db_sess.query(HelpRequests).filter(HelpRequests.status == 'open').all()
    db_sess.close()
    return render_template('admin_support_reply.html', user=current_user, requests=open_requests)


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

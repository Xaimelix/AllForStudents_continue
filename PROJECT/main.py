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
from werkzeug.utils import secure_filename
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
#app.config['SWAGGER_URL'] = '/apidocs' # URL для Swagger UI

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
                "name": "Application Eviction",
                "description": "Операции с заявками на выселение"
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
    db_sess = db_session.create_session()
    top_hostels = db_sess.query(Hostel).order_by(Hostel.id.desc()).limit(3).all()
    db_sess.close()
    return render_template("basepage.html", top_hostels=top_hostels[::-1])


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
        student_applications = db_sess.query(Application_request).filter(Application_request.student_id == current_user.id).all()
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


#@app.route('/apidocs')
#@admin_required
#def swagger_ui():
#    return render_template('flasgger_ui.html')


# страница общежитий
@app.route('/hostels')
def hostel():
    db_sess = db_session.create_session()
    hostels = db_sess.query(Hostel).all()
    
    free_places_by_hostel = {}
    
    for hostel in hostels:
        free_places_by_hostel[hostel.id] = 0
    
    # Получаем все комнаты
    rooms = db_sess.query(Room).all()
    
    for room in rooms:
        if room.hostel_id in free_places_by_hostel:
            free_places_by_hostel[room.hostel_id] += (room.max_cnt_student - room.cur_cnt_student)
    db_sess.close()
    return render_template('finding.html', 
                          hostels=hostels, 
                          free_places=free_places_by_hostel)


@app.route('/filter')
def room():
    return (render_template('application.html'))


@app.route('/rooms')
def test_rooms():
    session = db_session.create_session()

    hostel_id = request.args.get('hostel', type=int)
    min_square = request.args.get('min_square', type=int)
    max_square = request.args.get('max_square', type=int)
    max_students = request.args.get('max_students', type=int)
    sex_filter = request.args.get('sex', 'any')

    query = session.query(Room)

    if hostel_id:
        query = query.filter(Room.hostel_id == hostel_id)
    if min_square:
        query = query.filter(Room.square >= min_square)
    if max_square:
        query = query.filter(Room.square <= max_square)
    if max_students:
        query = query.filter(Room.max_cnt_student == max_students)
    if sex_filter != 'any':
        query = query.filter(Room.sex == int(sex_filter))

    rooms = query.all()
    hostels = session.query(Hostel).all()

    return render_template('filter.html',
                           rooms=rooms,
                           hostels=hostels,
                           current_filters=request.args)


@app.route('/book_room/<int:id>', methods=['GET', 'POST'])
def book_room(id):
    db_sess = db_session.create_session()

    if not current_user.is_authenticated:
        return redirect('/login')
    room = db_sess.query(Room).get(id)
    if not room:
        abort(404)
    student = db_sess.query(Student).get(current_user.id)
    if not student:
        abort(403)
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


@app.route('/application_eviction', methods=['GET', 'POST'])
@admin_required
def applications_eviction():
    db_sess = db_session.create_session()
    server_base_url = request.url_root
    if not server_base_url.endswith('/'):
        server_base_url += '/'
    # applications = db_sess.query(Application_Eviction).all()
    return render_template('application_eviction.html', user=current_user, server_url=server_base_url)


@app.route('/admin_support_reply', methods=['GET', 'POST'])
@admin_required
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

@app.route('/add_hostels', methods=['GET', 'POST'])
@admin_required
def add_hostels():
    if request.method == 'GET':
        return render_template('add_hostels.html')
    
    # Обработка POST-запроса
    address = request.form.get('address')
    district = request.form.get('district')
    description = request.form.get('description')
    
    db_sess = db_session.create_session()
    hostel = Hostel(
        address=address,
        district=district,
        description=description
    )
    db_sess.add(hostel)
    db_sess.commit()
    
    # Создаем папку для фотографий общежития
    hostel_dir = os.path.join(app.static_folder, 'images', 'Hostels', str(hostel.id))
    os.makedirs(hostel_dir, exist_ok=True)
    
    # Обрабатываем загрузку фотографий
    def save_photo(file, filename):
        if file and file.filename != '':
            file.save(os.path.join(hostel_dir, filename))
    
    save_photo(request.files['main_photo'], 'main.JPG')
    
    db_sess.close()
    return redirect('/admin')

@app.route('/add_rooms', methods=['GET', 'POST'])
@admin_required
def add_rooms():
    db_sess = db_session.create_session()
    
    if request.method == 'GET':
        hostels = db_sess.query(Hostel).all()
        return render_template('add_rooms.html', hostels=hostels)
    
    # Обработка POST-запроса
    hostel_id = int(request.form.get('hostel_id'))
    number_room = int(request.form.get('number_room'))
    square = request.form.get('square')
    max_cnt_student = request.form.get('max_cnt_student')
    floor = request.form.get('floor')
    sex = int(request.form.get('sex'))
    side = request.form.get('side')
    
    room = Room(
        hostel_id=hostel_id,
        square=square,
        max_cnt_student=max_cnt_student,
        cur_cnt_student=0,
        floor=floor,
        sex=sex,
        side=side,
        number_room=number_room
    )
    
    db_sess.add(room)
    db_sess.commit()
    
    # Создаем папку для фотографий комнаты
    room_dir = os.path.join(app.static_folder, 'images', 'Rooms', str(room.id))
    os.makedirs(room_dir, exist_ok=True)
    
    # Обрабатываем загрузку фотографий
    def save_photo(file, filename):
        if file and file.filename != '':
            file.save(os.path.join(room_dir, filename))
    
    save_photo(request.files['main_photo'], 'main.JPG')
    save_photo(request.files['bathroom_photo'], 'bathroom.JPG')
    save_photo(request.files['kitchen_photo'], 'kitchen.JPG')
    
    db_sess.close()
    return redirect('/admin')

@app.route('/help', methods=['GET', 'POST'])
def help_page():
    return render_template('help_page.html')


@login_required
@app.route('/start', methods=['GET', 'POST'])
def starter_page():
    """
    Стартовая страница приложения. Выбор пользователем как отправить заявку на общежитие (автоматическое распределение или фильтровать)
    """
    return render_template('starter.html', user=current_user)


@login_required
@app.route('/auto')
def auto():
    db_sess = db_session.create_session()
    server_base_url = request.url_root
    if not server_base_url.endswith('/'):
        server_base_url += '/'
    rooms = db_sess.query(Room).filter(Room.cur_cnt_student < Room.max_cnt_student, Room.sex == current_user.sex).all()
    for i in rooms:
        print(i.id)
    return redirect('/me')


def how_to_apply():
    """
    Страница с инструкцией по подаче заявки на общежитие
    """
    return render_template('how_to.html')


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

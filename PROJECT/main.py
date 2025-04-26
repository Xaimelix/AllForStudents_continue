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

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pfybvfqntcmcgjhnfvvfkmxbrbbltdjxrb'
login_manager = LoginManager()
login_manager.init_app(app)
swagger = Swagger(app)


def main():
    db_session.global_init("db/database.db")
    app.run()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(Student).get(user_id)


@app.route('/')
def main_page():
    if not current_user.is_authenticated:
        return "Hello world"
    return f"{current_user.name, current_user.surname}"


@app.route('/me')
def myself():
    if not current_user.is_authenticated:
        return redirect('/login')
    return f'thats my page'


@app.route('/hostel/<id>')
def hostel(id):
    return f'Hostel: {id}'


@app.route('/room/<id>')
def room(id):
    return f'Room: {id}'


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


@app.route('/settings')
def settings():
    return 'settings'


@app.route('/applications')
def admin():
    return 'applications'

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

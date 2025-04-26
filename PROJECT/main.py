from flask import Flask, redirect, render_template
from flask_login import login_user

from data import db_session
from data.student import Student
from form.loginform import LoginForm
from form.registrationform import RegistrationForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pfybvfqntcmcgjhnfvvfkmxbrbbltdjxrb'

def main():
    db_session.global_init("db/database.db")
    app.run()


@app.route('/')
def main_page():
    return "Hello world"


@app.route('/me')
def myself():
    return f'thats my page'


@app.route('/hostel/<id>')
def hostel(id):
    return f'Hostel: {id}'


@app.route('/room/<id>')
def room(id):
    return f'Room: {id}'


@app.route('/registration', methods=['GET', 'POST'])
def registration():
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
            surname=form.surname.data
        )

        student.set_password(form.password.data)
        db_sess.add(student)
        db_sess.commit()
        db_sess.close()
        return redirect('/')
    return render_template('registration.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
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


@app.route('/settings')
def settings():
    return 'settings'


@app.route('/admin')
def admin():
    return 'admin'


if __name__ == "__main__":
    main()

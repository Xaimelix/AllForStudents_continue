from flask_restful import Resource, reqparse
from flask import Flask, send_file
from data.db_session import create_session
from sqlalchemy import func
from data.application_request import Application_request
from data.student import Student
from data.room import Room
from data.hostel import Hostel
from datetime import datetime

import matplotlib

matplotlib.use('Agg')  # Используем 'Agg' для работы с графиками без GUI

import matplotlib.pyplot as plt
from fpdf import FPDF
import io

# --- Парсер для ApplicationRequestResource (для методов POST/PUT) ---
application_request_parser = reqparse.RequestParser()
application_request_parser.add_argument('status', type=str, required=True, help='Статус заявки обязателен', location=['json', 'form'])
application_request_parser.add_argument('room_id', type=int, required=True, help='ID комнаты обязателен', location=['json', 'form'])
application_request_parser.add_argument('student_id', type=int, required=True, help='ID студента обязателен', location=['json', 'form'])
application_request_parser.add_argument('date_entr', type=str, help='Дата въезда (YYYY-MM-DD)', location=['json', 'form'])
application_request_parser.add_argument('date_exit', type=str, help='Дата выезда (YYYY-MM-DD)', location=['json', 'form'])


# --- Новый класс для операций над коллекцией заявок ---
class ApplicationRequestsListResource(Resource):
    def get(self):
        """Получение списка всех заявок.
        ---
        tags:
          - Application Requests
        responses:
          200:
            description: Список заявок
            schema:
              type: object
              properties:
                requests:
                  type: array
                  items:
                    $ref: '#/definitions/ApplicationRequest'
          500:
            description: Ошибка при получении списка заявок
            schema:
              type: object
              properties:
                message:
                  type: string
        definitions: # Определение схемы заявки (можно вынести в отдельный файл схем)
          ApplicationRequest:
            type: object
            properties:
              id:
                type: integer
              status:
                type: string
              date_entr:
                type: string
                format: date
              date_exit:
                type: string
                format: date
              room_id:
                type: integer
              student_id:
                type: integer
              reject_reason:
                type: string
        """
        db_sess = create_session()
        try:
            requests = db_sess.query(Application_request).all()
            result = []
            for request in requests:
                result.append({
                    'id': request.id,
                    'status': request.status,
                    'date_entr': request.date_entr.strftime('%Y-%m-%d') if request.date_entr else None,
                    'date_exit': request.date_exit.strftime('%Y-%m-%d') if request.date_exit else None,
                    'room_id': request.room_id,
                    'student_id': request.student_id,
                    'reject_reason': request.reject_reason
                })
            return {'requests': result}, 200
        except Exception as e:
            return {'message': f'Ошибка при получении заявок: {e}'}, 500
        finally:
            db_sess.close()

    def post(self):
        """Создание новой заявки.
        ---
        tags:
          - Application Requests
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              properties:
                status:
                  type: string
                date_entr:
                  type: string
                  format: date
                date_exit:
                  type: string
                  format: date
                room_id:
                  type: integer
                student_id:
                  type: integer
        responses:
          201:
            description: Заявка успешно создана
            schema:
              type: object
              properties:
                message:
                  type: string
                request_id:
                  type: integer
          400:
            description: Неверный формат данных или даты
            schema:
              type: object
              properties:
                message:
                  type: string
          500:
            description: Ошибка при создании заявки
            schema:
              type: object
              properties:
                message:
                  type: string
        """
        args = application_request_parser.parse_args()

        date_entr = None
        date_exit = None

        try:
            if args['date_entr']:
                date_entr = datetime.strptime(args['date_entr'], '%Y-%m-%d').date()
            if args['date_exit']:
                date_exit = datetime.strptime(args['date_exit'], '%Y-%m-%d').date()
        except ValueError:
            return {'message': 'Неверный формат даты. Используйте<ctrl97>-MM-DD.'}, 400

        db_sess = create_session()
        try:
            new_request = Application_request(
                status=args['status'],
                date_entr=date_entr,
                date_exit=date_exit,
                room_id=args['room_id'],
                student_id=args['student_id']
            )
            db_sess.add(new_request)
            db_sess.commit()
            return {'message': 'Заявка успешно создана!', 'request_id': new_request.id}, 201
        except Exception as e:
            db_sess.rollback()
            return {'message': f'Ошибка при создании заявки: {e}'}, 500
        finally:
            db_sess.close()


application_put_parser = reqparse.RequestParser()
# Указываем, что ожидаем 'status' в теле запроса в формате JSON
application_put_parser.add_argument('status', type=str, help='Статус заявки обязателен', location=['json', 'form'])
application_put_parser.add_argument('room_id', type=int, help='ID комнаты обязателен', location=['json', 'form'])
application_put_parser.add_argument('student_id', type=int, help='ID студента обязателен', location=['json', 'form'])
application_put_parser.add_argument('date_entr', type=str, help='Дата въезда (YYYY-MM-DD)', location=['json', 'form'])
application_put_parser.add_argument('date_exit', type=str, help='Дата выезда (YYYY-MM-DD)', location=['json', 'form'])
application_put_parser.add_argument('reject_reason', type=str, help='Причина отклонения', location=['json', 'form'])

# --- Новый класс для операций над отдельной заявкой по ID ---
class ApplicationRequestItemResource(Resource):
    def get(self, request_id):
        """Получение информации о заявке по ID.
        ---
        tags:
          - Application Requests
        parameters:
          - name: request_id
            in: path
            type: integer
            required: true
            description: ID заявки
        responses:
          200:
            description: Информация о заявке
            schema:
              $ref: '#/definitions/ApplicationRequest'
          404:
            description: Заявка не найдена
            schema:
              type: object
              properties:
                message:
                  type: string
          500:
            description: Ошибка при получении заявки
            schema:
              type: object
              properties:
                message:
                  type: string
        """
        db_sess = create_session()
        try:
            request = db_sess.query(Application_request).filter(Application_request.id == request_id).first()
            if not request:
                return {'message': f'Заявка с ID {request_id} не найдена'}, 404

            result = {
                'id': request.id,
                'status': request.status,
                'date_entr': request.date_entr.strftime('%Y-%m-%d') if request.date_entr else None,
                'date_exit': request.date_exit.strftime('%Y-%m-%d') if request.date_exit else None,
                'room_id': request.room_id,
                'student_id': request.student_id,
                'reject_reason': request.reject_reason
            }
            return {'request': result}, 200

        except Exception as e:
            return {'message': f'Ошибка при получении заявки: {e}'}, 500
        finally:
            db_sess.close()

    def delete(self, request_id):
        """Удаление заявки по ID.
        ---
        tags:
          - Application Requests
        parameters:
          - name: request_id
            in: path
            type: integer
            required: true
            description: ID заявки
        responses:
          200:
            description: Заявка успешно удалена
            schema:
              type: object
              properties:
                message:
                  type: string
          404:
            description: Заявка не найдена
            schema:
              type: object
              properties:
                message:
                  type: string
          500:
            description: Ошибка при удалении заявки
            schema:
              type: object
              properties:
                message:
                  type: string
        """
        db_sess = create_session()
        try:
            request_to_delete = db_sess.query(Application_request).filter(Application_request.id == request_id).first()
            if not request_to_delete:
                return {'message': f'Заявка с ID {request_id} не найдена'}, 404

            db_sess.delete(request_to_delete)
            db_sess.commit()
            return {'message': f'Заявка с ID {request_id} успешно удалена'}, 200
        except Exception as e:
            db_sess.rollback()
            return {'message': f'Ошибка при удалении заявки с ID {request_id}: {e}'}, 500
        finally:
            db_sess.close()

    def put(self, request_id):
        """Обновление статуса заявки по ID.
        ---
        tags:
          - Application Requests
        parameters:
          - name: request_id
            in: path
            type: integer
            required: true
            description: ID заявки для обновления
          - name: body
            in: body
            schema:
              type: object
              properties:
                status:
                  type: string
                  description: Новый статус заявки ('1' для одобрения, '2' для отклонения)
                reject_reason:
                  type: string
                  description: Причина отклонения (если статус '2')
              required:
                - status
        responses:
          200:
            description: Статус заявки успешно обновлен
            schema:
              type: object
              properties:
                message:
                  type: string
          404:
            description: Заявка не найдена
            schema:
              type: object
              properties:
                message:
                  type: string
          400:
            description: Неверный формат данных или отсутствует статус
            schema:
              type: object
              properties:
                message:
                  type: string
          500:
            description: Ошибка при обновлении статуса заявки
            schema:
              type: object
              properties:
                message:
                  type: string
        """
        args = application_put_parser.parse_args(strict=False) # Используем новый парсер для статуса, strict=True для игнорирования других полей
        new_status = args.get('status') # Получаем новый статус
        new_room_id = args.get('room_id') # Получаем новый room_id
        new_student_id = args.get('student_id') # Получаем новый student_id
        new_date_entr = args.get('date_entr') # Получаем новую дату въезда
        new_date_exit = args.get('date_exit') # Получаем новую дату выезда
        reject_reason = args.get('reject_reason') # Получаем причину отклонения
        # Проверяем, что новый статус указан

        if new_status is None:
            return {'message': 'В теле запроса должен быть указан новый статус ("status").'}, 400

        # TODO: Добавь валидацию статуса, чтобы принимать только '1' или '2'
        if new_status not in ['1', '2']:
             return {'message': 'Неверное значение статуса. Допустимы только "1" (одобрено) или "2" (отклонено).'}, 400


        db_sess = create_session()
        try:
            # Ищем заявку по ID
            request_to_update = db_sess.query(Application_request).filter(Application_request.id == request_id).first()

            # Если заявка не найдена, возвращаем 404
            if not request_to_update:
                return {'message': f'Заявка с ID {request_id} не найдена'}, 404

            # Обновляем статус
            request_to_update.status = new_status
            if new_room_id is not None:
                request_to_update.room_id = new_room_id
            if new_student_id is not None:
                request_to_update.student_id = new_student_id
            if new_date_entr is not None:
                request_to_update.date_entr = datetime.strptime(new_date_entr, '%Y-%m-%d').date()
            if new_date_exit is not None:
                request_to_update.date_exit = datetime.strptime(new_date_exit, '%Y-%m-%d').date()
            if reject_reason is not None:
                request_to_update.reject_reason = reject_reason
            

            # Коммитим изменения
            db_sess.commit()

            # Возвращаем успешный ответ
            return {'message': f'Статус заявки с ID {request_id} успешно обновлен на "{new_status}"'}, 200

        except Exception as e:
            # Откатываем изменения в случае ошибки и возвращаем 500
            db_sess.rollback()
            return {'message': f'Ошибка при обновлении статуса заявки с ID {request_id}: {e}'}, 500
        finally:
            db_sess.close()

# --- Парсер для StudentListResource (для методов POST/PUT) ---
student_parser = reqparse.RequestParser()
student_parser.add_argument('login', type=str, required=True, help='Логин студента обязателен', location='form') 
student_parser.add_argument('hashed_password', type=str, required=True, help='Хэшированный пароль обязателен', location='form')
student_parser.add_argument('name', type=str, required=True, help='Имя студента обязательно', location='form')
student_parser.add_argument('surname', type=str, required=True, help='Фамилия студента обязательна', location='form')
student_parser.add_argument('room_id', type=int, help='ID комнаты', location='form') 
student_parser.add_argument('course', type=int, help='Курс студента', location='form')
student_parser.add_argument('about', type=str, help='О студенте', location='form')
student_parser.add_argument('sex', type=bool, help='Пол студента', location='form')

class StudentListResource(Resource):
    def post(self):
        """Создание нового студента.
        ---
        tags:
          - Students
        parameters:
          - name: login
            in: formData
            type: string
            required: true
            description: Логин студента
          - name: hashed_password
            in: formData
            type: string
            required: true
            description: Хэшированный пароль
          - name: name
            in: formData
            type: string
            required: trueF
            description: Имя студента
          - name: surname
            in: formData
            type: string
            required: true
            description: Фамилия студента
          - name: room_id
            in: formData
            type: integer
            required: false
            description: ID комнаты
          - name: course
            in: formData
            type: integer
            required: false
            description: Курс студента
          - name: about
            in: formData
            type: string
            required: false
            description: О студенте
          - name: sex
            in: formData
            type: boolean
            required: false
            description: Пол студента (True - мужской, False - женский)
        responses:
          201:
            description: Студент успешно создан
            schema:
              type: object
              properties:
                message:
                  type: string
                student_id:
                  type: integer
          500:
            description: Ошибка при создании студента
            schema:
              type: object
              properties:
                message:
                  type: string
        """
        args = student_parser.parse_args()
        db_sess = create_session()
        try:
            new_student = Student(
                login=args['login'],
                # TODO: Хэширование пароля должно происходить здесь или в модели
                hashed_password=args['hashed_password'], # В реальном приложении здесь нужно хэшировать пароль
                name=args['name'],
                surname=args['surname'],
                room_id=args['room_id'],
                course=args['course'],
                about=args['about'],
                sex=args['sex']
            )
            db_sess.add(new_student)
            db_sess.commit()
            # Возвращаем student_id, а не request_id
            return {'message': 'Студент успешно создан!', 'student_id': new_student.id}, 201
        except Exception as e:
            db_sess.rollback()
            # Исправлено сообщение об ошибке
            return {'message': f'Ошибка при создании студента: {e}'}, 500
        finally:
            db_sess.close()

    def get(self):
        """Получение списка всех студентов.
        ---
        tags:
          - Students
        responses:
          200:
            description: Список студентов
            schema:
              type: object
              properties:
                requests:
                  type: array
                  items:
                    $ref: '#/definitions/ApplicationRequest'
          500:
            description: Ошибка при получении списка студентов
            schema:
              type: object
              properties:
                message:
                  type: string
        definitions: # Определение схемы заявки (можно вынести в отдельный файл схем)
          Student:
            type: object
            properties:
              id:
                type: integer
              login:
                type: string
              name:
                type: string
                format: date
              surname:
                type: string
                format: date
              room_id:
                type: integer
              course:
                type: integer
              sex:
                type: boolean
              about:
                type: string
        """
        db_sess = create_session()
        students = db_sess.query(Student).all()
        result = []
        for student in students:
            result.append({
                'id': student.id,
                'login': student.login,
                'name': student.name,
                'surname': student.surname,
                'room_id': student.room_id,
                'course': student.course,
                'about': student.about,
                'sex': student.sex
            })
        return {'students': result}, 200
    


student_put_parser = reqparse.RequestParser()
# Указываем location='json' для всех полей, которые можно обновлять
# required=False для большинства полей, так как PUT может быть частичным обновлением
student_put_parser.add_argument('login', type=str, required=False, help='Новый логин студента', location='json')
student_put_parser.add_argument('name', type=str, required=False, help='Новое имя студента', location='json')
student_put_parser.add_argument('surname', type=str, required=False, help='Новая фамилия студента', location='json')
student_put_parser.add_argument('room_id', type=int, required=False, help='Новый ID комнаты', location='json')
student_put_parser.add_argument('course', type=int, required=False, help='Новый курс студента', location='json')
student_put_parser.add_argument('about', type=str, required=False, help='Новая информация о студенте', location='json')
student_put_parser.add_argument('sex', type=bool, required=False, help='Новый пол студента (True - мужской, False - женская)', location='json')

class StudentItemResource(Resource):
    def get(self, student_id):
        """Получение инф студенте по ID.
        ---
        tags:
          - Students
        parameters:
          - name: student_id
            in: path
            type: integer
            required: true  # Не обязателен, если получаем список всех студентов
            description: ID студента (для получения конкретного студента)
        responses:
          200:
            description: Список студентов или информация о студенте
            schema:
              type: object
              properties:
                students: # Для списка всех студентов
                  type: array
                  items:
                    $ref: '#/definitions/Student' # Ссылка на определение схемы студента
                student: # Для одного студента
                  $ref: '#/definitions/Student' # Ссылка на определение схемы студента
          404:
            description: Студент не найден (для запроса по ID)
            schema:
              type: object
              properties:
                message:
                  type: string
          500:
            description: Ошибка при получении студентов
            schema:
              type: object
              properties:
                message:
                  type: string
        definitions: # Определение схемы студента для Swagger
          Student:
            type: object
            properties:
              id:
                type: integer
              login:
                type: string
              name:
                type: string
              surname:
                type: string
              room_id:
                type: integer
                nullable: true # Соответствует nullable=True в модели
              course:
                type: integer
                nullable: true # Соответствует nullable=True в модели
              about:
                type: string
                nullable: true # Соответствует nullable=True в модели
              sex:
                type: boolean


        """
        db_sess = create_session()
            # Если ID предоставлен, возвращаем конкретного студента
        student = db_sess.query(Student).filter(Student.id == student_id).first()
        if not student:
            return {'message': f'Студент с ID {student_id} не найден'}, 404

        result = {
            'id': student.id,
            'login': student.login,
            'name': student.name,
            'surname': student.surname,
            'room_id': student.room_id,
            'course': student.course,
            'about': student.about,
            'sex': student.sex
        }
        return {'student': result}, 200
    
    def put(self, student_id):
        """Обновление информации о студенте по ID.
        ---
        tags:
          - Students
        parameters:
          - name: student_id
            in: path
            type: integer
            required: true
            description: ID студента для обновления
          - name: body # Описание тела запроса
            in: formData
            schema: # Схема ожидаемого JSON тела
              type: object
              properties:
                login:
                  type: string
                name:
                  type: string
                surname:
                  type: string
                room_id:
                  type: integer
                  nullable: true # Укажите nullable, если поле может быть None
                course:
                  type: integer
                  nullable: true # Укажите nullable, если поле может быть None
                about:
                  type: string
                  nullable: true # Укажите nullable, если поле может быть None
                sex:
                  type: boolean
                  nullable: true # Укажите nullable, если поле может быть None
              # required: # Можно указать поля, которые обязательны в теле запроса, но для частичного PUT это обычно не делают
              #  - course
        responses:
          200:
            description: Информация о студенте успешно обновлена
            schema:
              type: object
              properties:
                message:
                  type: string
          400:
            description: Неверный формат данных
            schema:
              type: object
              properties:
                message:
                  type: string
          404:
            description: Студент не найден
            schema:
              type: object
              properties:
                message:
                  type: string
          500:
            description: Ошибка при обновлении студента
            schema:
              type: object
              properties:
                message:
                  type: string
        """
    # Используем новый парсер для PUT запроса, который ожидает JSON
        # strict=False позволяет игнорировать поля в JSON, которых нет в парсере
        # (полезно, если клиент отправит больше данных, чем разрешено обновлять)
        args = student_put_parser.parse_args(strict=False)


        db_sess = create_session()
        try:
            # Ищем студента по ID
            student_to_update = db_sess.query(Student).filter(Student.id == student_id).first()

            # Если студент не найден, возвращаем 404
            if not student_to_update:
                return {'message': f'Студент с ID {student_id} не найден'}, 404

            # Обновляем поля студента только если они присутствуют в args (т.е. были переданы в запросе)
            # Это позволяет делать частичные обновления (например, менять только курс)

            if 'login' in args and args['login'] is not None:
                # TODO: Добавьте проверку на уникальность логина, если он был изменен
                student_to_update.login = args['login']

            if 'name' in args and args['name'] is not None:
                student_to_update.name = args['name']

            if 'surname' in args and args['surname'] is not None:
                student_to_update.surname = args['surname']

            if 'room_id' in args and args['room_id'] is not None:
                # TODO: Добавьте проверку на существование комнаты с таким ID
                student_to_update.room_id = args['room_id']
            # Специальная обработка для возможности установки room_id в None
            elif 'room_id' in args and args['room_id'] is None:
                student_to_update.room_id = None


            if 'course' in args and args['course'] is not None:
                student_to_update.course = args['course'] # <-- Обновление поля "course"
            # Специальная обработка для возможности установки course в None
            elif 'course' in args and args['course'] is None:
                student_to_update.course = None


            if 'about' in args and args['about'] is not None:
                student_to_update.about = args['about']
            # Специальная обработка для возможности установки about в None
            elif 'about' in args and args['about'] is None:
                student_to_update.about = None


            if 'sex' in args and args['sex'] is not None:
                student_to_update.sex = args['sex']

            # Коммитим изменения в базу данных
            db_sess.commit()

            # Возвращаем успешный ответ
            return {'message': f'Информация о студенте с ID {student_id} успешно обновлена'}, 200

        except Exception as e:
            # Откатываем изменения в случае ошибки и возвращаем 500
            db_sess.rollback()
            return {'message': f'Ошибка при обновлении студента с ID {student_id}: {e}'}, 500
        finally:
            db_sess.close()
    

    def delete(self, student_id):
        """Удаление студента по ID.
        ---
        tags:
          - Students
        parameters:
          - name: student_id
            in: path
            type: integer
            required: true
            description: ID студента
        responses:
          200:
            description: Студент успешно удален
            schema:
              type: object
              properties:
                message:
                  type: string
          404:
            description: Студент не найден
            schema:
              type: object
              properties:
                message:
                  type: string
          500:
            description: Ошибка при удалении студента
            schema:
              type: object
              properties:
                message:
                  type: string
        """
        # ID берется из аргумента метода, переданного из URL-пути
        db_sess = create_session()
        try:
            student_to_delete = db_sess.query(Student).filter(Student.id == student_id).first()
            if not student_to_delete:
                return {'message': f'Студент с ID {student_id} не найден'}, 404

            db_sess.delete(student_to_delete)
            db_sess.commit()
            return {'message': f'Студент с ID {student_id} успешно удален'}, 200
        except Exception as e:
            db_sess.rollback()
            return {'message': f'Ошибка при удалении студента с ID {student_id}: {e}'}, 500
        finally:
            db_sess.close()

room_parser = reqparse.RequestParser()
# Указываем location='json' для всех полей, которые можно обновлять
room_parser.add_argument('hostel_id', type=int, required=True, help='Номер общежития обязателен', location=['form', 'json'])
room_parser.add_argument('square', type=float, required=True, help='Площадь комнаты обязательна', location=['form', 'json'])
room_parser.add_argument('max_cnt_student', type=int, required=True, help='Максимальное количество студентов в комнате обязательно', location=['form', 'json'])
room_parser.add_argument('cur_cnt_student', type=int, required=True, help='Текущее количество студентов в комнате обязательно', location=['form', 'json'])
room_parser.add_argument('floor', type=int, required=True, help='Этаж комнаты обязателен', location=['form', 'json'])
room_parser.add_argument('sex', type=bool, required=True, help='Пол комнаты (True - мужская, False - женская) обязателен', location=['form', 'json'])
room_parser.add_argument('side', type=str, required=True, help='Сторона комнаты (например, "s - south", "n - north") обязательна', location=['form', 'json'])


# --- Новый класс для операций над коллекцией комнат ---
class RoomListResource(Resource):
    def get(self):
        """Получение списка всех комнат.
        ---
        tags:
            - Rooms
        responses:
          200:
            description: Список комнат
            schema:
              type: object
              properties:
                rooms: # Для списка всех комнат
                  type: array
                  items:
                    $ref: '#/definitions/Room' # Ссылка на определение схемы комнаты
          500:
            description: Ошибка при получении комнат
            schema:
              type: object
              properties:
                message:
                  type: string
        """
        db_sess = create_session()
        try:
            rooms = db_sess.query(Room).all()
            result = []
            for room in rooms:
                 result.append({
                    'id': room.id,
                    'hostel_id': room.hostel_id,
                    'square': room.square,
                    'max_cnt_student': room.max_cnt_student,
                    'cur_cnt_student': room.cur_cnt_student,
                    'floor': room.floor,
                    'sex': room.sex,
                    'side': room.side
                })
            return {'rooms': result}, 200
        except Exception as e:
            return {'message': f'Ошибка при получении комнат: {e}'}, 500
        finally:
            db_sess.close()


    def post(self):
        """
        Создание новой комнаты.
        ---
        tags:
          - Rooms
        consumes:
          - application/json
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              properties:
                hostel_id:
                  type: integer
                  description: Номер общежития
                square:
                  type: number
                  description: Площадь комнаты
                max_cnt_student:
                  type: integer
                  description: Максимальное количество студентов в комнате
                cur_cnt_student:
                  type: integer
                  description: Текущее количество студентов в комнате
                floor:
                  type: integer
                  description: Этаж комнаты
                sex:
                  type: boolean
                  description: Пол комнаты (True — мужская, False — женская)
                side:
                  type: string
                  description: Сторона комнаты (например, "s", "n", "e", "w")
              required:
                - hostel_id
                - square
                - max_cnt_student
                - cur_cnt_student
                - floor
                - sex
                - side
        responses:
          201:
            description: Комната успешно создана
            schema:
              type: object
              properties:
                message:
                  type: string
                room_id:
                  type: integer
          400:
            description: Неверные входные данные
            schema:
              type: object
              properties:
                message:
                  type: string
          500:
            description: Ошибка при создании комнаты
            schema:
              type: object
              properties:
                message:
                  type: string
        """
        args = room_parser.parse_args() # Используем room_parser
        db_sess = create_session()
        try:
            new_room = Room(
                hostel_id=args['hostel_id'],
                square=args['square'],
                max_cnt_student=args['max_cnt_student'],
                cur_cnt_student=args['cur_cnt_student'],
                floor=args['floor'],
                sex=args['sex'],
                side=args['side']
            )
            db_sess.add(new_room)
            db_sess.commit()
            return {'message': 'Комната успешно создана!', 'room_id': new_room.id}, 201
        except Exception as e:
            db_sess.rollback()
            return {'message': f'Ошибка при создании комнаты: {e}'}, 500
        finally:
            db_sess.close()


# --- Новый класс для операций над отдельной комнатой по ID ---
class RoomItemResource(Resource):
    def get(self, room_id):
        """Получение информации о комнате по ID.
        ---
        tags:
            - Rooms
        parameters:
          - name: room_id
            in: path
            type: integer
            required: true
            description: ID комнаты
        responses:
          200:
            description: Информация о комнате
            schema:
               $ref: '#/definitions/Room' # Ссылка на определение схемы комнаты
          404:
            description: Комната не найдена
            schema:
              type: object
              properties:
                message:
                  type: string
          500:
            description: Ошибка при получении комнаты
            schema:
              type: object
              properties:
                message:
                  type: string
        # Определения схем лучше делать один раз в конце файла
        # definitions:
        #   Room:
        #     ...
        """
        db_sess = create_session()
        try:
            room = db_sess.query(Room).filter(Room.id == room_id).first()
            if not room:
                return {'message': f'Комната с ID {room_id} не найдена'}, 404

            result = {
                'id': room.id,
                'hostel_id': room.hostel_id,
                'square': room.square,
                'max_cnt_student': room.max_cnt_student,
                'cur_cnt_student': room.cur_cnt_student,
                'floor': room.floor,
                'sex': room.sex,
                'side': room.side
            }
            return {'room': result}, 200
        except Exception as e:
            return {'message': f'Ошибка при получении комнаты: {e}'}, 500
        finally:
            db_sess.close()

    def put(self, room_id):
        """Обновление информации о комнате по ID.
        ---
        tags:
          - Rooms
        parameters:
          - name: room_id
            in: path
            type: integer
            required: true
            description: ID комнаты для обновления
          - name: body
            in: body
            schema:
              type: object
              properties:
                hostel_id:
                  type: integer
                square:
                  type: number
                max_cnt_student:
                  type: integer
                cur_cnt_student:
                  type: integer
                floor:
                  type: integer
                sex:
                  type: boolean
                side:
                  type: string
              required:
                - hostel_id
        responses:
          200:
            description: Информация о комнате успешно обновлена
            schema:
              type: object
              properties:
                message:
                  type: string
          400:
            description: Неверный формат данных
            schema:
              type: object
              properties:
                message:
                  type: string
          404:
            description: Комната не найдена
            schema:
              type: object
              properties:
                message:
                  type: string
          500:
            description: Ошибка при обновлении комнаты
            schema:
              type: object
              properties:
                message:
                  type: string
        """
        args = room_parser.parse_args()
        db_sess = create_session()
        try:
            # Ищем комнату по ID
            room_to_update = db_sess.query(Room).filter(Room.id == room_id).first()
            # Если комната не найдена, возвращаем 404
            if not room_to_update:
                return {'message': f'Комната с ID {room_id} не найдена'}, 404
            # Обновляем поля комнаты только если они присутствуют в args (т.е. были переданы в запросе)
            # Это позволяет делать частичные обновления (например, менять только площадь)
            if 'hostel_id' in args and args['hostel_id'] is not None:
                room_to_update.hostel_id = args['hostel_id']
            if 'square' in args and args['square'] is not None:
                room_to_update.square = args['square']
            if 'max_cnt_student' in args and args['max_cnt_student'] is not None:
                room_to_update.max_cnt_student = args['max_cnt_student']
            if 'cur_cnt_student' in args and args['cur_cnt_student'] is not None:
                room_to_update.cur_cnt_student = args['cur_cnt_student']
            if 'floor' in args and args['floor'] is not None:
                room_to_update.floor = args['floor']
            if 'sex' in args and args['sex'] is not None:
                room_to_update.sex = args['sex']
            if 'side' in args and args['side'] is not None:
                room_to_update.side = args['side']
            # Коммитим изменения
            db_sess.commit()
            # Возвращаем успешный ответ
            return {'message': f'Информация о комнате с ID {room_id} успешно обновлена'}, 200
        except Exception as e:
            # Откатываем изменения в случае ошибки и возвращаем 500
            db_sess.rollback()
            return {'message': f'Ошибка при обновлении комнаты с ID {room_id}: {e}'}, 500
        finally:
            db_sess.close()

    def delete(self, room_id):
        """Удаление комнаты по ID.
        ---
        tags:
            - Rooms
        parameters:
          - name: room_id
            in: path
            type: integer
            required: true
            description: ID комнаты
        responses:
          200:
            description: Комната успешно удалена
            schema:
              type: object
              properties:
                message:
                  type: string
          404:
            description: Комната не найдена
            schema:
              type: object
              properties:
                message:
                  type: string
          500:
            description: Ошибка при удалении комнаты
            schema:
              type: object
              properties:
                message:
                  type: string
        """
        # ID берется из аргумента метода, переданного из URL-пути
        db_sess = create_session()
        try:
            room_to_delete = db_sess.query(Room).filter(Room.id == room_id).first()
            if not room_to_delete:
                return {'message': f'Комната с ID {room_id} не найдена'}, 404

            db_sess.delete(room_to_delete)
            db_sess.commit()
            return {'message': f'Комната с ID {room_id} успешно удалена'}, 200
        except Exception as e:
            db_sess.rollback()
            return {'message': f'Ошибка при удалении комнаты с ID {room_id}: {e}'}, 500
        finally:
            db_sess.close()


    # TODO: Добавить метод put(self, room_id) для обновления комнаты

# --- Парсер для HostelResource (для методов POST/PUT) ---
hostel_parser = reqparse.RequestParser()
# !!! ДОБАВЛЕНО location='form' КО ВСЕМ АРГУМЕНТАМ ПАРСЕРА ОБЩЕЖИТИЙ !!!
hostel_parser.add_argument('address', type=str, required=True, help='Адрес общежития обязателен', location=['form', 'json'])
hostel_parser.add_argument('district', type=str, required=True, help='Район общежития обязателен', location=['form', 'json'])


# --- Новый класс для операций над коллекцией общежитий ---
class HostelListResource(Resource):
    def get(self):
        """Получение списка всех общежитий.
        ---
        tags:
            - Hostels
        responses:
          200:
            description: Список общежитий
            schema:
              type: object
              properties:
                hostels: # Для списка всех общежитий
                  type: array
                  items:
                    $ref: '#/definitions/Hostel' # Ссылка на определение схемы общежития
          500:
            description: Ошибка при получении общежитий
            schema:
              type: object
              properties:
                message:
                  type: string
        # Определения схем лучше делать один раз в конце файла
        # definitions:
        #   Hostel:
        #     ...
        """
        db_sess = create_session()
        try:
            hostels = db_sess.query(Hostel).all()
            result = []
            for hostel in hostels:
                result.append({
                    'id': hostel.id,
                    'address': hostel.address,
                    'district': hostel.district
                })
            return {'hostels': result}, 200
        except Exception as e:
            return {'message': f'Ошибка при получении общежитий: {e}'}, 500
        finally:
            db_sess.close()


    def post(self):
        """Создание нового общежития.
        ---
        tags:
          - Hostels
        consumes:
          - application/json
        parameters: 
          - in: body
            name: body
            required: true
            schema:
              type: object
              properties:
                address:
                  type: string
                  description: Адрес общежития
                district:
                  type: string
                  description: Район общежития
              required:
                - address
                - district
        responses:
          201:
            description: Общежитие успешно создано
            schema:
              type: object
              properties:
                message:
                  type: string
                hostel_id:
                  type: integer
          500:
            description: Ошибка при создании общежития
            schema:
              type: object
              properties:
                message:
                  type: string
        # Определения схем лучше делать один раз в конце файла
        # definitions:
        #   Hostel:
        #     ...
        """
        args = hostel_parser.parse_args()
        db_sess = create_session()
        try:
            new_hostel = Hostel(
                address=args['address'],
                district=args['district']
            )
            db_sess.add(new_hostel)
            db_sess.commit()
            return {'message': 'Общежитие успешно создано!', 'hostel_id': new_hostel.id}, 201
        except Exception as e:
            db_sess.rollback()
            return {'message': f'Ошибка при создании общежития: {e}'}, 500
        finally:
            db_sess.close()

# --- Новый класс для операций над отдельным общежитием по ID ---
class HostelItemResource(Resource):
    def get(self, hostel_id):
        """Получение информации о общежитии по ID.
        ---
        tags:
            - Hostels
        parameters:
          - name: hostel_id
            in: path
            type: integer
            required: true
            description: ID общежития
        responses:
          200:
            description: Информация о общежитии
            schema:
              $ref: '#/definitions/Hostel' # Ссылка на определение схемы общежития
          404:
            description: Общежитие не найдено
            schema:
              type: object
              properties:
                message:
                  type: string
          500:
            description: Ошибка при получении общежитий
            schema:
              type: object
              properties:
                message:
                  type: string
        # Определения схем лучше делать один раз в конце файла
        # definitions:
        #   Hostel:
        #     ...
        """
        db_sess = create_session()
        try:
            hostel = db_sess.query(Hostel).filter(Hostel.id == hostel_id).first()
            if not hostel:
                return {'message': f'Общежитие с ID {hostel_id} не найдено'}, 404

            result = {
                'id': hostel.id,
                'address': hostel.address,
                'district': hostel.district
            }
            return {'hostel': result}, 200
        except Exception as e:
            return {'message': f'Ошибка при получении общежитий: {e}'}, 500
        finally:
            db_sess.close()


    def delete(self, hostel_id):
        """Удаление общежития по ID.
        ---
        tags:
            - Hostels
        parameters:
          - name: hostel_id
            in: path
            type: integer
            required: true
            description: ID общежития
        responses:
          200:
            description: Общежитие успешно удалено
            schema:
              type: object
              properties:
                message:
                  type: string
          404:
            description: Общежитие не найдено
            schema:
              type: object
              properties:
                message:
                  type: string
          500:
            description: Ошибка при удалении общежития
            schema:
              type: object
              properties:
                message:
                  type: string
        """
        # ID берется из аргумента метода, переданного из URL-пути
        db_sess = create_session()
        try:
            hostel_to_delete = db_sess.query(Hostel).filter(Hostel.id == hostel_id).first()
            if not hostel_to_delete:
                return {'message': f'Общежитие с ID {hostel_id} не найдено'}, 404

            db_sess.delete(hostel_to_delete)
            db_sess.commit()
            return {'message': f'Общежитие с ID {hostel_id} успешно удалено'}, 200
        except Exception as e:
            db_sess.rollback()
            return {'message': f'Ошибка при удалении общежития с ID {hostel_id}: {e}'}, 500
        finally:
            db_sess.close()




class ReportResource(Resource):

    def get(self, report_type):
        """
        Генерация различных отчетов в формате PDF.
        ---
        tags:
          - Reports
        parameters:
          - name: report_type
            in: path
            type: string
            required: true
            description: Тип отчета (например, 'pdf', 'csv')
          # Могут быть другие параметры для фильтрации (например, hostel_id, start_date, end_date)
          # - name: hostel_id
          #   in: query
          #   type: integer
          #   required: false
          #   description: ID общежития для фильтрации
        responses:
          200:
            description: PDF отчет успешно сгенерирован
            schema:
              type: file # В Swagger 2.0 для файлов
              format: binary
              # Или в OpenAPI 3.0: content: {'application/pdf': {schema: {type: string, format: binary}}}
          400:
            description: Неизвестный тип отчета или некорректные параметры
            schema:
              type: object
              properties:
                message:
                  type: string
          500:
            description: Ошибка при генерации отчета
            schema:
              type: object
              properties:
                message:
                  type: string
        """
        if report_type == 'pdf':
            return self.generate_pdf_report()
        # elif report_type == 'csv':
            # return self.generate_csv_report()
        # Добавь другие типы отчетов по мере необходимости
        else:
            return {'message': f'Неизвестный тип отчета: {report_type}'}, 400

    def generate_pdf_report(self):
        """Логика генерации отчета по заполненности комнат."""
        db_sess = create_session()

        # --- 1. Сбор сводной статистики по общежитиям ---
        try:
            hostel_summary_data = db_sess.query(
                Hostel.id,
                Hostel.address,
                func.count(Room.id).label('total_rooms'), # Количество комнат в общежитии
                func.sum(Room.max_cnt_student).label('total_capacity'), # Общая максимальная вместимость
                func.sum(Room.cur_cnt_student).label('total_occupied') # Общее текущее количество студентов
            ).join(Room).group_by(Hostel.id, Hostel.address).all()
            # print(hostel_summary_data)

            # Результат будет списком кортежей или объектов, например:
            # [(hostel_id, address, total_rooms, total_capacity, total_occupied), ...]

            # Обработка данных для расчета свободных мест и процентов
            hostel_stats = []
            
            for hostel in hostel_summary_data:
                free_spots = hostel.total_capacity - hostel.total_occupied
                # Процент заполненности по общежитию
                occupancy_percentage = (hostel.total_occupied / hostel.total_capacity) * 100 if hostel.total_capacity > 0 else 0

                hostel_stats.append({
                    'id': hostel.id,
                    'address': hostel.address,
                    'total_rooms': hostel.total_rooms,
                    'total_capacity': hostel.total_capacity,
                    'total_occupied': hostel.total_occupied,
                    'free_spots': free_spots,
                    'occupancy_percentage': occupancy_percentage,
                    'total_capacity': hostel.total_capacity
                })

            #--- 2. Сбор данных о популярных комнатах ---
            try:
                # Получаем все комнаты с их текущим количеством студентов, привязанные к общежитию
                rooms_with_occupancy = db_sess.query(
                    Hostel.id.label('hostel_id'),
                    Hostel.address,
                    Room.id.label('room_id'),
                    Room.cur_cnt_student
                ).join(Hostel).filter(Room.cur_cnt_student > 0).order_by(Hostel.id, Room.cur_cnt_student.desc()).all() # Сортируем по общежитию и убыванию студентов

                # Группируем по общежитиям и выбираем, например, топ-N самых "занятых" комнат в каждом
                popular_rooms_by_hostel = {}
                current_hostel_id = None
                top_n = 3 # Например, хотим показать топ-3 самых занятых комнат в каждом общежитии
                for room in rooms_with_occupancy:
                    if room.hostel_id not in popular_rooms_by_hostel:
                        popular_rooms_by_hostel[room.hostel_id] = {
                            'address': room.address,
                            'rooms': []
                        }

                    if len(popular_rooms_by_hostel[room.hostel_id]['rooms']) < top_n:
                        popular_rooms_by_hostel[room.hostel_id]['rooms'].append({
                            'room_id': room.room_id,
                            'cur_cnt_student': room.cur_cnt_student
                        })


                # Теперь popular_rooms_by_hostel - это словарь, где ключи - ID общежитий, а значения - информация о самых занятых комнатах.

            except Exception as e:
                print(f"Ошибка при сборе данных о комнатах для популярности: {e}")
            
            # --- 4. Создание круговых диаграмм для каждого общежития и добавление их в PDF ---
            pdf = FPDF()
            # try:
            #     font_path = 'PROJECT/static/fonts/DejaVuSans.ttf' # Путь к шрифту DejaVuSans.ttf
            #     pdf.add_font('DejaVuSans', '', font_path, uni=True)
            #     pdf.set_font('DejaVuSans', '', 12)
            # except RuntimeError:
            pdf.set_font("Arial", size=12) # Вернуться к стандартному, если шрифт не работает
            # if hostel['id'] in popular_rooms_by_hostel:
            
            #     pdf.cell(0, 10, txt="Самые занятые комнаты:", ln=True, align='L')
            #     for room in popular_rooms_by_hostel[hostel['id']]['rooms']:
            #         # Здесь можно добавить текст для каждой комнаты, например:
            #         pdf.cell(0, 10, txt=f"Комната ID {room['room_id']}: {room['cur_cnt_student']} студентов", ln=True, align='L')
            #         pdf.ln(5) # Небольшой отступ после информации о комнатах

            
            for hostel in hostel_stats:
                pdf.add_page()
                # Данные для круговой диаграммы: занятые места и свободные места
                sizes = [hostel['total_occupied'], hostel['free_spots']]
                labels = ['Занято', 'Свободно']
                colors = ['#ff9999','#66b3ff'] # Цвета для секторов
                # Если в общежитии нет мест (capacity = 0) или 0 студентов, диаграмма может быть некорректной.
                # Добавим простую проверку.
                if hostel['total_capacity'] == 0:
                    print(f"Общежитие {hostel['address']} имеет 0 вместимость, диаграмма не будет построена.")
                    continue # Пропускаем это общежитие

                if hostel['total_occupied'] == 0 and hostel['free_spots'] == 0:
                    print(f"Общежитие {hostel['address']} имеет 0 студентов и 0 свободных мест, диаграмма не будет построена.")
                    continue # Пропускаем это общежитие

                plt.figure(figsize=(6, 6)) # Размер фигуры для диаграммы
                plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
                plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                plt.title(f"Filiness of the hostel: {hostel['address']}") # Заголовок диаграммы

                if hostel['id'] in popular_rooms_by_hostel:
                    pdf.cell(0, 10, txt="The most popular rooms:", ln=True, align='L')
                    for room in popular_rooms_by_hostel[hostel['id']]['rooms']:
                        # Здесь можно добавить текст для каждой комнаты, например:
                        pdf.cell(0, 10, txt=f"Room {room['room_id']}: {room['cur_cnt_student']} students", ln=True, align='L')
                        pdf.ln(5) # Небольшой отступ после информации о комнатах



                # Сохраняем диаграмму в байты
                img_buffer = io.BytesIO()
                plt.savefig(img_buffer, format='png')
                img_buffer.seek(0)
                plt.close() # Закрываем фигуру Matplotlib

                # Добавляем заголовок общежития в PDF
                # Убедимся, что используем шрифт с кириллицей, если он успешно добавлен

                pdf.cell(0, 10, txt=f"Hostel: {hostel['address']}", ln=True, align='L')
                # Добавляем изображение диаграммы в PDF
                # w=100 - пример ширины изображения, можешь настроить под свой формат страницы
                pdf.image(img_buffer, x=None, y=None, w=100)                
                pdf.ln(10) # Отступ после диаграммы
                pdf.cell(0, 10, txt=f"Total capacity: {hostel['total_capacity']}", ln=True, align='L')

            
            pdf_output = pdf.output(dest='S') # TODO: Возможно, 'utf-8' или другой кодек с поддержкой кириллицы, если настроены шрифты

            # 5. Отправка PDF
            return send_file(io.BytesIO(pdf_output),
                            mimetype='application/pdf',
                            as_attachment=True,
                            download_name='report.pdf')

        except Exception as e:
            return {'message': f'Ошибка при создании отчета: {e}'}, 500
        finally:
            db_sess.close()

# TODO: Добавить if на отправку csv файла в зависимости от report_type
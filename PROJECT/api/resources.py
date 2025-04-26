from flask_restful import Resource, reqparse
from PROJECT.data.db_session import create_session
from PROJECT.data.application_request import Application_request
from PROJECT.data.student import Student
from PROJECT.data.room import Room
from PROJECT.data.hostel import Hostel
from datetime import datetime

# --- Парсер для ApplicationRequestResource (для методов POST/PUT) ---
application_request_parser = reqparse.RequestParser()
application_request_parser.add_argument('status', type=str, required=True, help='Статус заявки обязателен')
application_request_parser.add_argument('date_entr', type=str, help='Дата въезда (YYYY-MM-DD)')
application_request_parser.add_argument('date_exit', type=str, help='Дата выезда (YYYY-MM-DD)')
application_request_parser.add_argument('room_id', type=int, required=True, help='ID комнаты обязателен')
application_request_parser.add_argument('student_id', type=int, required=True, help='ID студента обязателен')


class ApplicationRequestResource(Resource):

    def post(self):
        """Создание новой заявки.
        ---
        tags:
          - Application Requests
        parameters:
          - name: status
            in: formData
            type: string
            required: true
            description: Статус заявки
          - name: date_entr
            in: formData
            type: string
            required: false
            description: Дата въезда (YYYY-MM-DD)
          - name: date_exit
            in: formData
            type: string
            required: false
            description: Дата выезда (YYYY-MM-DD)
          - name: room_id
            in: formData
            type: integer
            required: true
            description: ID комнаты
          - name: student_id
            in: formData
            type: integer
            required: true
            description: ID студента
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
            return {'message': 'Неверный формат даты. Используйте YYYY-MM-DD.'}, 400

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

    def get(self, request_id=None):
        """Получение списка всех заявок или информации о заявке по ID.
        ---
        tags:
          - Application Requests
        parameters:
          - name: request_id
            in: path
            type: integer
            required: false # Не обязателен, если получаем список всех заявок
            description: ID заявки (для получения конкретной заявки)
        responses:
          200:
            description: Список заявок или информация о заявке
            schema:
              type: object
              properties:
                requests: # Для списка всех заявок
                  type: array
                  items:
                    $ref: '#/definitions/ApplicationRequest' # Ссылка на определение схемы заявки
                request: # Для одной заявки
                  $ref: '#/definitions/ApplicationRequest' # Ссылка на определение схемы заявки
          404:
            description: Заявка не найдена (для запроса по ID)
            schema:
              type: object
              properties:
                message:
                  type: string
          500:
            description: Ошибка при получении заявок
            schema:
              type: object
              properties:
                message:
                  type: string
        definitions: # Определение схемы заявки для Swagger
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

        """
        db_sess = create_session()
        try:
            if request_id is None:
                # Если ID не предоставлен, возвращаем список всех заявок
                requests = db_sess.query(Application_request).all()
                result = []
                for request in requests:
                    result.append({
                        'id': request.id,
                        'status': request.status,
                        'date_entr': request.date_entr.strftime('%Y-%m-%d') if request.date_entr else None,
                        'date_exit': request.date_exit.strftime('%Y-%m-%d') if request.date_exit else None,
                        'room_id': request.room_id,
                        'student_id': request.student_id
                    })
                return {'requests': result}, 200
            else:
                # Если ID предоставлен, возвращаем конкретную заявку
                request = db_sess.query(Application_request).filter(Application_request.id == request_id).first()
                if not request:
                    return {'message': f'Заявка с ID {request_id} не найдена'}, 404
                
                result = {
                    'id': request.id,
                    'status': request.status,
                    'date_entr': request.date_entr.strftime('%Y-%m-%d') if request.date_entr else None,
                    'date_exit': request.date_exit.strftime('%Y-%m-%d') if request.date_exit else None,
                    'room_id': request.room_id,
                    'student_id': request.student_id
                }
                return {'request': result}, 200

        except Exception as e:
            return {'message': f'Ошибка при получении заявок: {e}'}, 500
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
        # ID берется из аргумента метода, переданного из URL-пути
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

    # TODO: Добавить метод put(self, request_id) для обновления заявки


# --- Парсер для StudentResource (для методов POST/PUT) ---
student_parser = reqparse.RequestParser()
student_parser.add_argument('login', type=str, required=True, help='Логин студента обязателен')
student_parser.add_argument('hashed_password', type=str, required=True, help='Хэшированный пароль обязателен')
student_parser.add_argument('name', type=str, required=True, help='Имя студента обязательно')
student_parser.add_argument('surname', type=str, required=True, help='Фамилия студента обязательна')
student_parser.add_argument('room_id', type=int, help='ID комнаты')
student_parser.add_argument('course', type=int, help='Курс студента')
student_parser.add_argument('about', type=str, help='О студенте')
student_parser.add_argument('sex', type=bool, help='Пол студента') # TODO: Возможно, лучше использовать 'true'/'false' строки и преобразовывать


class StudentResource(Resource):
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
            required: true
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
                student_id: # Исправлено с request_id на student_id
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

    def get(self, student_id=None):
        """Получение списка всех студентов или информации о студенте по ID.
        ---
        tags:
          - Students
        parameters:
          - name: student_id
            in: path
            type: integer
            required: false # Не обязателен, если получаем список всех студентов
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
        try:
            if student_id is None:
                # Если ID не предоставлен, возвращаем список всех студентов
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
            else:
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
        except Exception as e:
            return {'message': f'Ошибка при получении студента: {e}'}, 500
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

    # TODO: Добавить метод put(self, student_id) для обновления студента


# --- Парсер для RoomResource (для методов POST/PUT) ---
room_parser = reqparse.RequestParser()
room_parser.add_argument('hostel_id', type=int, required=True, help='Номер общежития обязателен')
room_parser.add_argument('square', type=float, required=True, help='Площадь комнаты обязательна')
room_parser.add_argument('max_cnt_student', type=int, required=True, help='Максимальное количество студентов в комнате обязательно')
room_parser.add_argument('cur_cnt_student', type=int, required=True, help='Текущее количество студентов в комнате обязательно')
room_parser.add_argument('floor', type=int, required=True, help='Этаж комнаты обязателен')
room_parser.add_argument('sex', type=bool, required=True, help='Пол комнаты (True - мужская, False - женская) обязателен')
room_parser.add_argument('side', type=str, required=True, help='Сторона комнаты (например, "s - south", "n - north") обязательна')


class RoomResource(Resource):
    def post(self):
        """Создание новой комнаты.
        ---
        tags:
          - Rooms
        parameters:
          - name: hostel_id
            in: formData
            type: integer
            required: true
            description: Номер общежития
          - name: square
            in: formData
            type: number # Для float в Swagger используется number
            required: true
            description: Площадь комнаты
          - name: max_cnt_student
            in: formData
            type: integer
            required: true
            description: Максимальное количество студентов в комнате
          - name: cur_cnt_student
            in: formData
            type: integer
            required: true
            description: Текущее количество студентов в комнате
          - name: floor
            in: formData
            type: integer
            required: true
            description: Этаж комнаты
          - name: sex
            in: formData
            type: boolean
            required: true
            description: Пол комнаты (True - мужская, False - женская)
          - name: side
            in: formData
            type: string
            required: true
            description: Сторона комнаты (например, "s - south", "n - north")
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

    def get(self, room_id=None):
        """Получение списка всех комнат или информации о комнате по ID.
        ---
        tags:
            - Rooms
        parameters:
          - name: room_id
            in: path
            type: integer
            required: false # Не обязателен, если получаем список всех комнат
            description: ID комнаты (для получения конкретной комнаты)
        responses:
          200:
            description: Список комнат или информация о комнате
            schema:
              type: object
              properties:
                rooms: # Для списка всех комнат
                  type: array
                  items:
                    $ref: '#/definitions/Room' # Ссылка на определение схемы комнаты
                room: # Для одной комнаты
                   $ref: '#/definitions/Room' # Ссылка на определение схемы комнаты
          404:
            description: Комната не найдена (для запроса по ID)
            schema:
              type: object
              properties:
                message:
                  type: string
          500:
            description: Ошибка при получении комнат
            schema:
              type: object
              properties:
                message:
                  type: string
        definitions: # Определение схемы комнаты для Swagger
          Room:
            type: object
            properties:
              id:
                type: integer
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
        """
        db_sess = create_session()
        try:
            if room_id is None:
                # Если ID не предоставлен, возвращаем список всех комнат
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
            else:
                # Если ID предоставлен, возвращаем конкретную комнату
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
hostel_parser.add_argument('address', type=str, required=True, help='Адрес общежития обязателен')
hostel_parser.add_argument('district', type=str, required=True, help='Район общежития обязателен')


class HostelResource(Resource):
    def get(self, hostel_id=None):
        """Получение списка всех общежитий или информации о общежитии по ID.
        ---
        tags:
            - Hostels
        parameters:
          - name: hostel_id
            in: path
            type: integer
            required: false # Не обязателен, если получаем список всех общежитий
            description: ID общежития (для получения конкретного общежития)
        responses:
          200:
            description: Список общежитий или информация о общежитии
            schema:
              type: object
              properties:
                hostels: # Для списка всех общежитий
                  type: array
                  items:
                    $ref: '#/definitions/Hostel' # Ссылка на определение схемы общежития
                hostel: # Для одного общежития
                  $ref: '#/definitions/Hostel' # Ссылка на определение схемы общежития
          404:
            description: Общежитие не найдено (для запроса по ID)
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
        definitions: # Определение схемы общежития для Swagger
          Hostel:
            type: object
            properties:
              id:
                type: integer
              address:
                type: string
              district:
                type: string
        """
        db_sess = create_session()
        try:
            if hostel_id is None:
                # Если ID не предоставлен, возвращаем список всех общежитий
                hostels = db_sess.query(Hostel).all()
                result = []
                for hostel in hostels:
                    result.append({
                        'id': hostel.id,
                        'address': hostel.address,
                        'district': hostel.district
                    })
                return {'hostels': result}, 200
            else:
                # Если ID предоставлен, возвращаем конкретное общежитие
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


    def post(self):
        """Создание нового общежития.
        ---
        tags:
            - Hostels
        parameters:
          - name: address
            in: formData
            type: string
            required: true
            description: Адрес общежития
          - name: district
            in: formData
            type: string
            required: true
            description: Район общежития
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

    # TODO: Добавить метод put(self, hostel_id) для обновления общежития
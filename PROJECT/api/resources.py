from flask_restful import Resource, reqparse
from data.db_session import create_session
from data.application_request import Application_request
from data.student import Student
from data.room import Room
from data.hostel import Hostel
from flask_restful import Api, Resource, reqparse
from datetime import datetime

# Парсер для входящих аргументов POST/PUT запросов
parser = reqparse.RequestParser()
parser.add_argument('status', type=str, required=True, help='Статус заявки обязателен')
parser.add_argument('date_entr', type=str)
parser.add_argument('date_exit', type=str)
parser.add_argument('room_id', type=int, required=True, help='ID комнаты обязателен')
parser.add_argument('student_id', type=int, required=True, help='ID студента обязателен')

class ApplicationRequestResource(Resource):

    def post(self):
        """
        Создание новой заявки
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
          400:
            description: Неверный формат даты
          500:
            description: Ошибка при создании заявки
        """
        args = parser.parse_args()

        try:
            date_entr = datetime.strptime(args['date_entr'], '%Y-%m-%d').date()
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

    def get(self):
        """Получение списка всех заявок.
        ---
        tags:
            - Application Requests
        responses:
            200:
                description: Список заявок
            500:
                description: Ошибка при получении списка заявок
            404:
                description: Заявки не найдены
            """
        db_sess = create_session()
        requests = db_sess.query(Application_request).all()
        result = []
        for request in requests:
            result.append({
                'id': request.id,
                'status': request.status,
                'date_entr': request.date_entr.strftime('%Y-%m-%d'),
                'date_exit': request.date_exit.strftime('%Y-%m-%d'),
                'room_id': request.room_id,
                'student_id': request.student_id
            })
        db_sess.close()
        return {'requests': result}, 200

    def delete(self, request_id):
        """Удаление заявки.
        ---
        tags:
            - Application Requests
            parameters:
             - name: id
                in: query
                type: integer
                required: true
                description: ID заявки
            responses:
                200:
                    description: Заявка успешно удалена
                500:
                    description: Ошибка при удалении заявки
                404:
                    description: Заявка не найдена"""
        args = parser.parse_args()
        request_id = args.get('id')

        db_sess = create_session()
        request_to_delete = db_sess.query(Application_request).filter(Application_request.id == request_id).first()
        if not request_to_delete:
            return {'message': 'Заявка не найдена'}, 404

        try:
            db_sess.delete(request_to_delete)
            db_sess.commit()
            return {'message': 'Заявка успешно удалена'}, 200
        except Exception as e:
            db_sess.rollback()
            return {'message': f'Ошибка при удалении заявки: {e}'}, 500
        finally:
            db_sess.close()
    

student_parser = reqparse.RequestParser()
student_parser.add_argument('login', type=str, required=True, help='Логин студента обязателен')
student_parser.add_argument('hashed_password', type=str, required=True, help='Хэшированный пароль обязателен')
student_parser.add_argument('name', type=str, required=True, help='Имя студента обязательно')
student_parser.add_argument('surname', type=str, required=True, help='Фамилия студента обязательна')
student_parser.add_argument('room_id', type=int, help='ID комнаты')
student_parser.add_argument('course', type=int, help='Курс студента')
student_parser.add_argument('about', type=str, help='О студенте')
student_parser.add_argument('sex', type=bool, help='Пол студента')

# class StudentResource(Resource):
#     def post(self):
#         """Создание нового студента.
#         ---
#         tags:
#             - Students
#             parameters:
#             - name: login
#                 in: formData
#                 type: string
#                 required: true
#                 description: Логин студента
#             - name: hashed_password
#                 in: formData
#                 type: string
#                 required: true
#                 description: Хэшированный пароль
#             - name: name
#                 in: formData
#                 type: string
#                 required: true
#                 description: Имя студента
#             - name: surname
#                 in: formData
#                 type: string
#                 required: true
#                 description: Фамилия студента
#             - name: room_id
#                 in: formData
#                 type: integer
#                 required: false
#                 description: ID комнаты
#             - name: course
#                 in: formData
#                 type: integer
#                 required: false
#                 description: Курс студента
#             - name: about
#                 in: formData
#                 type: string
#                 required: false
#                 description: О студенте
#             - name: sex
#                 in: formData
#                 type: boolean
#                 required: false
#                 description: Пол студента (True - мужской, False - женский)
#             responses:
#                 201:
#                     description: Студент успешно создан
#                 500:
#                     description: Ошибка при создании студента"""
        
#         args = student_parser.parse_args()
#         db_sess = create_session()
#         try:
#             new_student = Student(
#                 login=args['login'],
#                 hashed_password=args['hashed_password'],
#                 name=args['name'],
#                 surname=args['surname'],
#                 room_id=args['room_id'],
#                 course=args['course'],
#                 about=args['about'],
#                 sex=args['sex']
#             )
#             db_sess.add(new_student)
#             db_sess.commit()
#             return {'message': 'Студент успешно создан!', 'request_id': new_student.id}, 201
#         except Exception as e:
#             db_sess.rollback()
#             return {'message': f'Ошибка при создании заявки: {e}'}, 500
#         finally:
#             db_sess.close()

#     def get(self, student_id):
#         """Получение информации о студенте по ID.
#         ---
#         tags:
#             - Students
#             parameters:
#             - name: id
#                 in: query
#                 type: integer
#                 required: true
#                 description: ID студента
#             responses:
#                 200:
#                     description: Информация о студенте
#                 404:
#                     description: Студент не найден
#         """
#         db_sess = create_session()
#         student = db_sess.query(Student).filter(Student.id == student_id).first()
#         if not student:
#             return {'message': 'Студент не найден'}, 404

#         result = {
#             'id': student.id,
#             'name': student.name,
#             'login': student.login,
#             'surname': student.surname,
#             'room_id': student.room_id,
#             'course': student.course,
#             'about': student.about,

#         }
#         db_sess.close()
#         return {'student': result}, 200
    
#     def delete(self, student_id):
#         """Удаление студента.
#         ---
#         tags:
#             - Students
#             parameters:
#             - name: id
#                 in: query
#                 type: integer
#                 required: true
#                 description: ID студента
#             responses:
#                 200:
#                     description: Студент успешно удален
#         """
#         db_sess = create_session()
#         student_to_delete = db_sess.query(Student).filter(Student.id == student_id).first()
#         if not student_to_delete:
#             return {'message': 'Студент не найден'}, 404

#         try:
#             db_sess.delete(student_to_delete)
#             db_sess.commit()
#             return {'message': 'Студент успешно удален'}, 200
#         except Exception as e:
#             db_sess.rollback()
#             return {'message': f'Ошибка при удалении студента: {e}'}, 500
#         finally:
#             db_sess.close()
    

room_parser = reqparse.RequestParser()

room_parser.add_argument('square', type=float, required=True, help='Площадь комнаты обязательна')
room_parser.add_argument('hostel_id', type=int, required=True, help='Номер общежития')
room_parser.add_argument('max_cnt_student', type=int, required=True, help='Максимальное количество студентов в комнате')
room_parser.add_argument('cur_cnt_student', type=int, required=True, help='Текущее количество студентов в комнате')
room_parser.add_argument('floor', type=int, required=True, help='Этаж комнаты')
room_parser.add_argument('sex', type=bool, required=True, help='Пол комнаты (True - мужская, False - женская)')
room_parser.add_argument('side', type=str, required=True, help='Сторона комнаты (например, "s - south", "n - north")')


class RoomResource(Resource):
    def post(self):
        """
        Добавление новой комнаты
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
          201:
            description: -_-
        Создание новой комнаты."""
        args = parser.parse_args()
        db_sess = create_session()
        try:
            new_room = Room(
                square=args['square'],
                max_cnt_student=args['max_cnt_student'],
                cur_cnt_student=args['cur_cnt_student'],
                floor=args['floor'],
                hostel_id=args['hostel_id'],
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

    def get(self, room_id):
        """Получение информации о комнате по ID.
        ---
        tags:
            - Rooms
            parameters:
            - name: id
                in: query
                type: integer
                required: true
                description: ID комнаты
            responses:
                200:
                    description: Информация о комнате
                404:
                    description: Комната не найдена"""
        db_sess = create_session()
        room = db_sess.query(Room).filter(Room.id == room_id).first()
        if not room:
            return {'message': 'Комната не найдена'}, 404

        result = {
            'id': room.id,
            'square': room.square,
            'max_cnt_student': room.max_cnt_student,
            'cur_cnt_student': room.cur_cnt_student,
            'floor': room.floor,
            'hostel_id': room.hostel_id,
            'sex': room.sex,
            'side': room.side
        }
        db_sess.close()
        return {'room': result}, 200
    
    def delete(self, room_id):
        """Удаление комнаты.
        ---
        tags:
            - Rooms
            parameters:
            - name: id
                in: query
                type: integer
                required: true
                description: ID комнаты
            responses:
                200:
                    description: Комната успешно удалена
                500:
                    description: Ошибка при удалении комнаты
                404:
                    description: Комната не найдена"""
        db_sess = create_session()
        room_to_delete = db_sess.query(Room).filter(Room.id == room_id).first()
        if not room_to_delete:
            return {'message': 'Комната не найдена'}, 404

        try:
            db_sess.delete(room_to_delete)
            db_sess.commit()
            return {'message': 'Комната успешно удалена'}, 200
        except Exception as e:
            db_sess.rollback()
            return {'message': f'Ошибка при удалении комнаты: {e}'}, 500
        finally:
            db_sess.close()



# hostel_parser = reqparse.RequestParser()
# hostel_parser.add_argument('address', type=str, required=True, help='Адрес общежития обязателен')
# hostel_parser.add_argument('district', type=str, required=True, help='Район общежития обязателен')


# class HostelResource(Resource):
#     def get(self, hostel_id):
#         """Получение информации о общежитии по ID.
#         parameters:
#           - name: id
#             in: query
#             type: integer
#             required: true
#           - name: hostel_id
#             in: query
#             type: integer
#             required: true
#           - name: square
#             in: query
#             type: integer
#             required: true
#           - name: max_cnt_student
#             in: query
#             type: integer
#             required: true
#           - name: cur_cnt_student
#             in: query
#             type: integer
#             required: true
#           - name: floor
#             in: query
#             type: integer
#             required: true
#           - name: sex
#             in: query
#             type: boolean
#             required: true
#           - name: side
#             in: query
#             type: string
#             required: true
#         responses:
#           201:
#             description: -_-
#         """
#         db_sess = create_session()
#         hostel = db_sess.query(Hostel).filter(Hostel.id == hostel_id).first()
#         if not hostel:
#             return {'message': 'Общежитие не найдено'}, 404

#         result = {
#             'id': hostel.id,
#             'address': hostel.address,
#             'district': hostel.district
#         }
#         db_sess.close()
#         return {'hostel': result}, 200
    
#     def post(self):
#         """Создание нового общежития.
#         ---
#         parameters:
#           - name: address
#             in: query
#             type: string
#             required: true
#           - name: district
#             in: query
#             type: string
#             required: true
#         responses:
#           201:
#             description: -_-
#         """
#         args = hostel_parser.parse_args()
#         db_sess = create_session()
#         try:
#             new_hostel = Hostel(
#                 address=args['address'],
#                 district=args['district']
#             )
#             db_sess.add(new_hostel)
#             db_sess.commit()
#             return {'message': 'Общежитие успешно создано!', 'hostel_id': new_hostel.id}, 201
#         except Exception as e:
#             db_sess.rollback()
#             return {'message': f'Ошибка при создании общежития: {e}'}, 500
#         finally:
#             db_sess.close()
    
#     def delete(self, hostel_id):
#         """Удаление общежития.
#         ---
#         tags:
#             - Hostels
#             parameters:
#             - name: id
#                 in: query
#                 type: integer
#                 required: true
#                 description: ID общежития
#             responses:
#                 200:
#                     description: Общежитие успешно удалено
#                 500:
#                     description: Ошибка при удалении общежития
#                 404:
#                     description: Общежитие не найдено"""
#         db_sess = create_session()
#         hostel_to_delete = db_sess.query(Hostel).filter(Hostel.id == hostel_id).first()
#         if not hostel_to_delete:
#             return {'message': 'Общежитие не найдено'}, 404

#         try:
#             db_sess.delete(hostel_to_delete)
#             db_sess.commit()
#             return {'message': 'Общежитие успешно удалено'}, 200
#         except Exception as e:
#             db_sess.rollback()
#             return {'message': f'Ошибка при удалении общежития: {e}'}, 500
#         finally:
#             db_sess.close()
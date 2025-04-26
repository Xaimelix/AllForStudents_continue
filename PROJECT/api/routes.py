from flask_restful import Api
from .resources import ApplicationRequestResource, RoomResource, StudentResource, HostelResource

def initialize_routes(api):
    """Инициализация маршрутов API."""
    # Для ApplicationRequestResource
    api.add_resource(ApplicationRequestResource, '/api/application_requests', endpoint='application_requests')
    api.add_resource(ApplicationRequestResource, '/api/application_requests/<int:request_id>', endpoint='application_request_by_id')

    # Для StudentResource
    api.add_resource(StudentResource, '/api/students', endpoint='students')
    api.add_resource(StudentResource, '/api/students/<int:student_id>', endpoint='student_by_id')

    # Для RoomResource
    api.add_resource(RoomResource, '/api/rooms', endpoint='rooms')
    api.add_resource(RoomResource, '/api/rooms/<int:room_id>', endpoint='room_by_id')

    # Для HostelResource
    api.add_resource(HostelResource, '/api/hostels', endpoint='hostels')
    api.add_resource(HostelResource, '/api/hostels/<int:hostel_id>', endpoint='hostel_by_id')
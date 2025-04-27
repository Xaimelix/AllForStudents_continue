from flask_restful import Api
from .resources import ApplicationRequestsListResource, ApplicationRequestItemResource, RoomItemResource, RoomListResource, StudentItemResource, StudentListResource, HostelItemResource, HostelListResource, ReportResource

def initialize_routes(api):
    """Инициализация маршрутов API."""
    # Для ApplicationRequestResource
    # Маршруты для Application Requests
    # Связываем ApplicationRequestsListResource с маршрутом без ID
    api.add_resource(ApplicationRequestsListResource, '/api/application_requests')
    # Связываем ApplicationRequestItemResource с маршрутом с ID
    api.add_resource(ApplicationRequestItemResource, '/api/application_requests/<int:request_id>')

    # Для StudentResource
    api.add_resource(StudentListResource, '/api/students', endpoint='students')
    api.add_resource(StudentItemResource, '/api/students/<int:student_id>', endpoint='student_by_id')

    # Для RoomResource
    api.add_resource(RoomListResource, '/api/rooms', endpoint='rooms')
    api.add_resource(RoomItemResource, '/api/rooms/<int:room_id>', endpoint='room_by_id')

    # Для HostelResource
    api.add_resource(HostelListResource, '/api/hostels', endpoint='hostels')
    api.add_resource(HostelItemResource, '/api/hostels/<int:hostel_id>', endpoint='hostel_by_id')

    # Для ReportResource
    api.add_resource(ReportResource, '/api/reports/<string:report_type>')
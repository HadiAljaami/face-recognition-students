from flask import Blueprint, request, jsonify
from services.exam_distribution_service import ExamService
from flasgger import swag_from

exam_routes = Blueprint('exam_routes', __name__)
exam_service = ExamService()

@exam_routes.route('/exams', methods=['GET'])
@swag_from({
    'responses': {200: {'description': 'List all exams'}},
    'tags': ['Exams']
})
def get_exams():
    exams = exam_service.get_all_exams()
    return jsonify(exams)

@exam_routes.route('/exam/<string:student_number>', methods=['GET'])
@swag_from({
    'parameters': [{'name': 'student_number', 'in': 'path', 'type': 'string', 'required': True}],
    'responses': {200: {'description': 'Get exam by student number'}},
    'tags': ['Exams']
})
def get_exam(student_number):
    exam = exam_service.find_exam_by_student_number(student_number)
    return jsonify(exam) if exam else (jsonify({'error': 'Exam not found'}), 404)

@exam_routes.route('/exam', methods=['POST'])
@swag_from({
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'student_number': {'type': 'string'},
                'subject': {'type': 'string'},
                'seat_number': {'type': 'string'},
                'exam_room': {'type': 'string'},
                'exam_center': {'type': 'string'},
                'exam_datetime': {'type': 'string', 'format': 'date-time'},
                'duration': {'type': 'integer'}
            }
        }
    }],
    'responses': {201: {'description': 'Exam added successfully'}, 400: {'description': 'Invalid input'}},
    'tags': ['Exams']
})
def add_exam():
    try:
        data = request.get_json()
        required_fields = ["student_number", "subject", "seat_number", "exam_room", "exam_center", "exam_datetime", "duration"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        exam_service.add_exam(**data)
        return jsonify({'message': 'Exam added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exam_routes.route('/exam/<string:student_number>', methods=['PUT'])
@swag_from({
    'parameters': [
        {'name': 'student_number', 'in': 'path', 'type': 'string', 'required': True},
        {'name': 'body', 'in': 'body', 'schema': {
            'type': 'object',
            'properties': {
                'subject': {'type': 'string'},
                'seat_number': {'type': 'string'},
                'exam_room': {'type': 'string'},
                'exam_center': {'type': 'string'},
                'exam_datetime': {'type': 'string', 'format': 'date-time'},
                'duration': {'type': 'integer'}
            }
        }}
    ],
    'responses': {
        200: {'description': 'Exam updated successfully'},
        400: {'description': 'Invalid input'},
        404: {'description': 'Exam not found'}
    },
    'tags': ['Exams']
})
def update_exam(student_number):
    try:
        data = request.get_json()

        # الحصول على بيانات الامتحان الحالية
        current_exam = exam_service.find_exam_by_student_number(student_number)
        if not current_exam:
            return jsonify({'error': 'Exam not found'}), 404

        # تحديث فقط الحقول الموجودة في الطلب، وإبقاء البقية كما هي
        updated_data = {}
        for field in ["subject", "seat_number", "exam_room", "exam_center", "exam_datetime", "duration"]:
            if field in data:  # إذا تم إرسال الحقل، قم بتحديثه حتى لو كان `None`
                updated_data[field] = data[field]
            else:
                updated_data[field] = current_exam[field]  # إبقاء القيمة القديمة

        # تنفيذ عملية التحديث
        exam_service.update_exam(student_number, **updated_data)
        return jsonify({'message': 'Exam updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exam_routes.route('/exam/<string:student_number>', methods=['DELETE'])
@swag_from({
    'parameters': [{'name': 'student_number', 'in': 'path', 'type': 'string', 'required': True}],
    'responses': {200: {'description': 'Exam deleted successfully'}},
    'tags': ['Exams']
})
def delete_exam(student_number):
    exam_service.delete_exam_by_student_number(student_number)
    return jsonify({'message': 'Exam deleted successfully'})

@exam_routes.route('/exam/id/<int:exam_id>', methods=['DELETE'])
@swag_from({
    'parameters': [{'name': 'exam_id', 'in': 'path', 'type': 'integer', 'required': True}],
    'responses': {200: {'description': 'Exam deleted successfully'}},
    'tags': ['Exams']
})
def delete_exam_by_id(exam_id):
    exam_service.delete_exam_by_id(exam_id)
    return jsonify({'message': 'Exam deleted successfully'})

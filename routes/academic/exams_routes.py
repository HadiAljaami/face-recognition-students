from flask import Blueprint, request, jsonify
from flasgger import swag_from
from services.academic.exams_service import ExamsService
from datetime import datetime, date, time
import json

exams_bp = Blueprint('exams', __name__, url_prefix='/api/academic/exams')
service = ExamsService()


SWAGGER_TEMPLATE = {
    'definitions': {
        'Exam': {
            'type': 'object',
            'properties': {
                'exam_id': {'type': 'integer', 'example': 1},
                'course_id': {'type': 'integer', 'example': 1},
                'major_id': {'type': 'integer', 'example': 1},
                'college_id': {'type': 'integer', 'example': 1},
                'level_id': {'type': 'integer', 'example': 1},
                'year_id': {'type': 'integer', 'example': 1},
                'semester_id': {'type': 'integer', 'example': 1},
                'exam_date': {'type': 'string', 'format': 'date', 'example': '2023-12-15'},
                'exam_time': {'type': 'string', 'format': 'time', 'example': '09:00:00'},
                'created_at': {
                    'type': 'string', 
                    'format': 'date-time',
                    'readOnly': True  # هذا يخبر Swagger أن الحقل للقراءة فقط
                }
            },
            'required': [
                'course_id', 'major_id', 'college_id', 
                'level_id', 'year_id', 'semester_id'
            ]
        }
    }
}
def merge_swagger(config):
    return {**config, **SWAGGER_TEMPLATE}


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        if isinstance(obj, time):
            return obj.strftime('%H:%M:%S')
        return super().default(obj)

def serialize_exam(exam):
    """Convert exam object to JSON-serializable dictionary"""
    if exam is None:
        return None
    
    return {
        'exam_id': exam.get('exam_id'),
        'course_id': exam.get('course_id'),
        'major_id': exam.get('major_id'),
        'college_id': exam.get('college_id'),
        'level_id': exam.get('level_id'),
        'year_id': exam.get('year_id'),
        'semester_id': exam.get('semester_id'),
        'exam_date': exam.get('exam_date').isoformat() if exam.get('exam_date') else None,
        'exam_time': exam.get('exam_time').strftime('%H:%M:%S') if exam.get('exam_time') else None,
        'created_at': exam.get('created_at').isoformat() if exam.get('created_at') else None
    }

# تسجيل المُشفر المخصص في تطبيق Flask
def init_app(app):
    app.json_encoder = DateTimeEncoder

@swag_from(merge_swagger({
    'tags': ['Academic - Exams'],
    'description': 'Create new exam',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            '$ref': '#/definitions/Exam'
        }
    }],
    'responses': {
        201: {'description': 'Created', 'schema': {'$ref': '#/definitions/Exam'}},
        400: {'description': 'Validation error'},
        404: {'description': 'Reference not found'},
        500: {'description': 'Server error'}
    }
}))
@exams_bp.route('/', methods=['POST'])
def create_exam():
    data = request.get_json()
    try:
        exam_date = datetime.strptime(data['exam_date'], '%Y-%m-%d').date() if data.get('exam_date') else None
        exam_time = datetime.strptime(data['exam_time'], '%H:%M:%S').time() if data.get('exam_time') else None
        
        result = service.create_exam(
            course_id=data['course_id'],
            major_id=data['major_id'],
            college_id=data['college_id'],
            level_id=data['level_id'],
            year_id=data['year_id'],
            semester_id=data['semester_id'],
            exam_date=exam_date,
            exam_time=exam_time
        )
        
        # استخدام دالة التحويل الموحدة
        return jsonify(serialize_exam(result)), 201
        
    except ValueError as e:
        code = 404 if "Invalid reference" in str(e) else 400
        return jsonify({'error': str(e)}), code
    except Exception as e:
        return jsonify({'error': 'Server error', 'details': str(e)}), 500

@exams_bp.route('/filter', methods=['GET'])
@swag_from(merge_swagger({
    'tags': ['Academic - Exams'],
    'description': 'Filter exams by criteria',
    'parameters': [
        {
            'name': 'major_id',
            'in': 'query',
            'type': 'integer',
            'required': False
        },
        {
            'name': 'college_id',
            'in': 'query',
            'type': 'integer',
            'required': False
        },
        {
            'name': 'level_id',
            'in': 'query',
            'type': 'integer',
            'required': False
        },
        {
            'name': 'year_id',
            'in': 'query',
            'type': 'integer',
            'required': False
        },
        {
            'name': 'semester_id',
            'in': 'query',
            'type': 'integer',
            'required': False
        }
    ],
    'responses': {
        200: {
            'description': 'List of filtered exams',
            'schema': {
                'type': 'array',
                'items': {'$ref': '#/definitions/Exam'}
            }
        },
        400: {'description': 'Invalid filter parameters'},
        500: {'description': 'Server error'}
    }
}))
def filter_exams():
    try:
        # التعديل هنا: تحويل القيم بشكل صحيح
        major_id = request.args.get('major_id', type=int) if 'major_id' in request.args else None
        college_id = request.args.get('college_id', type=int) if 'college_id' in request.args else None
        level_id = request.args.get('level_id', type=int) if 'level_id' in request.args else None
        year_id = request.args.get('year_id', type=int) if 'year_id' in request.args else None
        semester_id = request.args.get('semester_id', type=int) if 'semester_id' in request.args else None
        
        results = service.filter_exams(
            major_id=major_id,
            college_id=college_id,
            level_id=level_id,
            year_id=year_id,
            semester_id=semester_id
        )
        
        serialized_results = [serialize_exam(exam) for exam in results]
        return jsonify(serialized_results), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Server error', 'details': str(e)}), 500
# Add these endpoints to the existing controller

@exams_bp.route('/<int:exam_id>', methods=['PUT'])
@swag_from({
    'tags': ['Academic - Exams'],
    'description': 'Update exam details',
    'parameters': [
        {
            'name': 'exam_id',
            'in': 'path',
            'type': 'integer',
            'required': True
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                '$ref': '#/definitions/Exam'
            }
        }
    ],
    'responses': {
        200: {'description': 'Updated exam', 'schema': {'$ref': '#/definitions/Exam'}},
        400: {'description': 'Validation error'},
        404: {'description': 'Exam not found'},
        500: {'description': 'Server error'}
    }
})
def update_exam(exam_id):
    data = request.get_json()
    try:
        # التحويل والتحقق
        exam_date = (
            datetime.strptime(data['exam_date'], '%Y-%m-%d').date() 
            if data.get('exam_date') else None
        )
        exam_time = (
            datetime.strptime(data['exam_time'], '%H:%M:%S').time() 
            if data.get('exam_time') else None
        )

        # استدعاء الخدمة
        result = service.update_exam(
            exam_id=exam_id,
            course_id=data['course_id'],
            major_id=data['major_id'],
            college_id=data['college_id'],
            level_id=data['level_id'],
            year_id=data['year_id'],
            semester_id=data['semester_id'],
            exam_date=exam_date,
            exam_time=exam_time
        )

        return jsonify(serialize_exam(result)), 200

    except ValueError as e:
        code = 404 if "not found" in str(e) else 400
        return jsonify({'error': str(e)}), code
    except RuntimeError as e:
        return jsonify({
            'error': 'Database operation failed',
            'details': str(e),
            'solution': 'Please try again later'
        }), 503
    except Exception as e:
        return jsonify({
            'error': 'Server error',
            'details': str(e),
            'reference': f"ERR-{datetime.now().timestamp()}"
        }), 500

@exams_bp.route('/', methods=['DELETE'])
@swag_from(merge_swagger({
    'tags': ['Academic - Exams'],
    'description': 'Delete multiple exams',
    'parameters': [{
        'name': 'exam_ids',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'exam_ids': {
                    'type': 'array',
                    'items': {'type': 'integer'},
                    'example': [1, 2, 3]
                }
            },
            'required': ['exam_ids']
        }
    }],
    'responses': {
        200: {
            'description': 'Deletion result',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'deleted_count': {'type': 'integer'}
                }
            }
        },
        400: {'description': 'Validation error'},
        404: {'description': 'No exams found'},
        500: {'description': 'Server error'}
    }
}))
def delete_exams():
    try:
        data = request.get_json()
        if not data or 'exam_ids' not in data:
            raise ValueError("Exam IDs array is required")
        
        result = service.delete_exams(data['exam_ids'])
        return jsonify(result), 200
    except ValueError as e:
        code = 404 if "No exams found" in str(e) else 400
        return jsonify({'error': str(e)}), code
    except Exception as e:
        return jsonify({'error': 'Server error', 'details': str(e)}), 500
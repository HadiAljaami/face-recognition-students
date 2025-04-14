from flask import Blueprint, request, jsonify
from flasgger import swag_from
from services.academic.exams_service import ExamsService
from services.academic.exams_excel_service import ExamsExcelService
from datetime import datetime, date, time
import json
from io import BytesIO
import os

exams_bp = Blueprint('exams', __name__, url_prefix='/api/academic/exams')
service = ExamsService()
excel = ExamsExcelService()

SWAGGER_TEMPLATE = {
    'definitions': {
        'Exam': {
            'type': 'object',
            'properties': {
                # للحقول المسطحة (للاستخدام في الإدخال)
                'course_id': {'type': 'integer', 'example': 1},
                'major_id': {'type': 'integer', 'example': 1},
                'college_id': {'type': 'integer', 'example': 1},
                'level_id': {'type': 'integer', 'example': 1},
                'year_id': {'type': 'integer', 'example': 1},
                'semester_id': {'type': 'integer', 'example': 1},
                'exam_date': {'type': 'string', 'format': 'date', 'example': '2023-12-15'},
                'exam_start_time': {'type': 'string', 'format': 'time', 'example': '09:00:00'},
                'exam_end_time': {'type': 'string', 'format': 'time', 'example': '11:00:00'},
                
                # للحقول المتداخلة (للاستخدام في الإخراج)
                'exam_id': {'type': 'integer', 'example': 1, 'readOnly': True},
                'course': {
                    'type': 'object',
                    'properties': {
                        'course_id': {'type': 'integer', 'readOnly': True},
                        'course_name': {'type': 'string', 'readOnly': True}
                    },
                    'readOnly': True
                },
                'major': {
                    'type': 'object',
                    'properties': {
                        'major_id': {'type': 'integer', 'readOnly': True},
                        'major_name': {'type': 'string', 'readOnly': True}
                    },
                    'readOnly': True
                },
                # ... نفس النمط لباقي الحقول ...
                'created_at': {'type': 'string', 'format': 'date-time', 'readOnly': True}
            },
            'required': ['course_id', 'major_id', 'college_id', 'level_id', 'year_id', 'semester_id']
        }
    }
}

def merge_swagger(config):
    return {**config, **SWAGGER_TEMPLATE}

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime, time)):
            return obj.isoformat()
        return super().default(obj)

def serialize_exam(exam):
    """Convert exam object to JSON-serializable dictionary with nested objects"""
    if exam is None:
        return None
    
    return {
        'exam_id': exam.get('exam_id'),
        'course': {
            'course_id': exam.get('course_id'),
            'course_name': exam.get('course_name')
        },
        'major': {
            'major_id': exam.get('major_id'),
            'major_name': exam.get('major_name')
        },
        'college': {
            'college_id': exam.get('college_id'),
            'college_name': exam.get('college_name')
        },
        'level': {
            'level_id': exam.get('level_id'),
            'level_name': exam.get('level_name')
        },
        'year': {
            'year_id': exam.get('year_id'),
            'year_name': exam.get('year_name')
        },
        'semester': {
            'semester_id': exam.get('semester_id'),
            'semester_name': exam.get('semester_name')
        },
        'exam_date': exam.get('exam_date').isoformat() if exam.get('exam_date') else None,
        'exam_start_time': exam.get('exam_start_time').isoformat() if exam.get('exam_start_time') else None,
        'exam_end_time': exam.get('exam_end_time').isoformat() if exam.get('exam_end_time') else None,
        'created_at': exam.get('created_at').isoformat() if exam.get('created_at') else None
    }

def init_app(app):
    app.json_encoder = DateTimeEncoder

@exams_bp.route('/', methods=['POST'])
@swag_from(merge_swagger({
    'tags': ['Academic - Exams'],
    'description': 'Create new exam',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'course_id': {'type': 'integer', 'example': 1},
                'major_id': {'type': 'integer', 'example': 1},
                'college_id': {'type': 'integer', 'example': 1},
                'level_id': {'type': 'integer', 'example': 1},
                'year_id': {'type': 'integer', 'example': 1},
                'semester_id': {'type': 'integer', 'example': 1},
                'exam_date': {'type': 'string', 'format': 'date', 'example': '2023-12-15'},
                'exam_start_time': {'type': 'string', 'format': 'time', 'example': '09:00:00'},
                'exam_end_time': {'type': 'string', 'format': 'time', 'example': '11:00:00'}
            },
            'required': ['course_id', 'major_id', 'college_id', 'level_id', 'year_id', 'semester_id']
        }
    }],
    'responses': {
        201: {'description': 'Created', 'schema': {'$ref': '#/definitions/Exam'}},
        400: {'description': 'Validation error'},
        404: {'description': 'Reference not found'},
        500: {'description': 'Server error'}
    }
}))
def create_exam():
    data = request.get_json()
    try:
        # Parse date and times
        exam_date = datetime.strptime(data['exam_date'], '%Y-%m-%d').date() if data.get('exam_date') else None
        exam_start_time = datetime.strptime(data['exam_start_time'], '%H:%M:%S').time() if data.get('exam_start_time') else None
        exam_end_time = datetime.strptime(data['exam_end_time'], '%H:%M:%S').time() if data.get('exam_end_time') else None
        
        result = service.create_exam(
            course_id=data['course_id'],
            major_id=data['major_id'],
            college_id=data['college_id'],
            level_id=data['level_id'],
            year_id=data['year_id'],
            semester_id=data['semester_id'],
            exam_date=exam_date,
            exam_start_time=exam_start_time,
            exam_end_time=exam_end_time
        )
        
        return jsonify(serialize_exam(result)), 201
        
    except ValueError as e:
        code = 404 if "Invalid reference" in str(e) else 400
        return jsonify({'error': str(e)}), code
    except Exception as e:
        return jsonify({'error': 'Server error', 'details': str(e)}), 500
#-----------------filter using post-------------------------------

# @exams_bp.route('/filter', methods=['POST'])  # تغيير من GET إلى POST
# @swag_from(merge_swagger({
#     'tags': ['Academic - Exams'],
#     'description': 'Filter exams by criteria',
#     'parameters': [{
#         'name': 'filters',
#         'in': 'body',
#         'required': False,
#         'schema': {
#             'type': 'object',
#             'properties': {
#                 'major_id': {'type': 'integer', 'example': 1},
#                 'college_id': {'type': 'integer', 'example': 1},
#                 'level_id': {'type': 'integer', 'example': 1},
#                 'year_id': {'type': 'integer', 'example': 1},
#                 'semester_id': {'type': 'integer', 'example': 1},
#                 'exam_date': {'type': 'string', 'format': 'date', 'example': '2023-12-15'},
#                 'start_time': {'type': 'string', 'format': 'time', 'example': '09:00:00'},
#                 'end_time': {'type': 'string', 'format': 'time', 'example': '11:00:00'}
#             }
#         }
#     }],
#     'responses': {
#         200: {
#             'description': 'List of filtered exams',
#             'schema': {
#                 'type': 'array',
#                 'items': {'$ref': '#/definitions/Exam'}
#             }
#         },
#         400: {'description': 'Invalid filter parameters'},
#         500: {'description': 'Server error'}
#     }
# }))
# def filter_exams():
#     data = request.get_json() or {}  # الحصول على البيانات ككائن JSON
#     try:
#         # Parse date and times
#         filters = {
#             'major_id': data.get('major_id'),
#             'college_id': data.get('college_id'),
#             'level_id': data.get('level_id'),
#             'year_id': data.get('year_id'),
#             'semester_id': data.get('semester_id'),
#             'exam_date': datetime.strptime(data['exam_date'], '%Y-%m-%d').date() if data.get('exam_date') else None,
#             'start_time': datetime.strptime(data['start_time'], '%H:%M:%S').time() if data.get('start_time') else None,
#             'end_time': datetime.strptime(data['end_time'], '%H:%M:%S').time() if data.get('end_time') else None
#         }
        
#         # إزالة القيم الفارغة
#         filters = {k: v for k, v in filters.items() if v is not None}
        
#         results = service.filter_exams(**filters)
#         return jsonify([serialize_exam(exam) for exam in results]), 200
        
#     except ValueError as e:
#         return jsonify({'error': str(e)}), 400
#     except Exception as e:
#         return jsonify({'error': 'Server error', 'details': str(e)}), 500

#------------------------------------------------
@exams_bp.route('/filter', methods=['GET'])
@swag_from(merge_swagger({
    'tags': ['Academic - Exams'],
    'description': 'Filter exams by criteria',
    'parameters': [
        {'name': 'major_id', 'in': 'query', 'type': 'integer', 'required': False},
        {'name': 'college_id', 'in': 'query', 'type': 'integer', 'required': False},
        {'name': 'level_id', 'in': 'query', 'type': 'integer', 'required': False},
        {'name': 'year_id', 'in': 'query', 'type': 'integer', 'required': False},
        {'name': 'semester_id', 'in': 'query', 'type': 'integer', 'required': False},
        {'name': 'exam_date', 'in': 'query', 'type': 'string', 'format': 'date', 'required': False},
        {'name': 'start_time', 'in': 'query', 'type': 'string', 'format': 'time', 'required': False},
        {'name': 'end_time', 'in': 'query', 'type': 'string', 'format': 'time', 'required': False}
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
        # Parse query parameters
        major_id = request.args.get('major_id', type=int)
        college_id = request.args.get('college_id', type=int)
        level_id = request.args.get('level_id', type=int)
        year_id = request.args.get('year_id', type=int)
        semester_id = request.args.get('semester_id', type=int)
        
        # Parse date/time parameters
        exam_date = datetime.strptime(request.args['exam_date'], '%Y-%m-%d').date() if 'exam_date' in request.args else None
        start_time = datetime.strptime(request.args['start_time'], '%H:%M:%S').time() if 'start_time' in request.args else None
        end_time = datetime.strptime(request.args['end_time'], '%H:%M:%S').time() if 'end_time' in request.args else None
        
        results = service.filter_exams(
            major_id=major_id,
            college_id=college_id,
            level_id=level_id,
            year_id=year_id,
            semester_id=semester_id,
            exam_date=exam_date,
            start_time=start_time,
            end_time=end_time
        )
        
        return jsonify([serialize_exam(exam) for exam in results]), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Server error', 'details': str(e)}), 500

#------------------------------------------------

@exams_bp.route('/<int:exam_id>', methods=['PUT'])
@swag_from(merge_swagger({
    'tags': ['Academic - Exams'],
    'description': 'Update exam details',
    'parameters': [
        {
            'name': 'exam_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the exam to update'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'course_id': {'type': 'integer', 'example': 1, 'required': False},
                    'major_id': {'type': 'integer', 'example': 1, 'required': False},
                    'college_id': {'type': 'integer', 'example': 1, 'required': False},
                    'level_id': {'type': 'integer', 'example': 1, 'required': False},
                    'year_id': {'type': 'integer', 'example': 1, 'required': False},
                    'semester_id': {'type': 'integer', 'example': 1, 'required': False},
                    'exam_date': {'type': 'string', 'format': 'date', 'example': '2023-12-15', 'required': False},
                    'exam_start_time': {'type': 'string', 'format': 'time', 'example': '09:00:00', 'required': False},
                    'exam_end_time': {'type': 'string', 'format': 'time', 'example': '11:00:00', 'required': False}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Exam updated successfully',
            'schema': {'$ref': '#/definitions/Exam'}
        },
        400: {'description': 'Validation error or invalid input data'},
        404: {'description': 'Exam not found or invalid reference IDs'},
        500: {'description': 'Internal server error'}
    }
}))
def update_exam(exam_id):
    data = request.get_json()
    try:
        # Parse date and times if provided
        exam_date = datetime.strptime(data['exam_date'], '%Y-%m-%d').date() if data.get('exam_date') else None
        exam_start_time = datetime.strptime(data['exam_start_time'], '%H:%M:%S').time() if data.get('exam_start_time') else None
        exam_end_time = datetime.strptime(data['exam_end_time'], '%H:%M:%S').time() if data.get('exam_end_time') else None

        # Call the service to update the exam
        result = service.update_exam(
            exam_id=exam_id,
            course_id=data.get('course_id'),
            major_id=data.get('major_id'),
            college_id=data.get('college_id'),
            level_id=data.get('level_id'),
            year_id=data.get('year_id'),
            semester_id=data.get('semester_id'),
            exam_date=exam_date,
            exam_start_time=exam_start_time,
            exam_end_time=exam_end_time
        )

        if not result:
            raise ValueError("Exam not found")

        return jsonify(serialize_exam(result)), 200

    except ValueError as e:
        # Determine if it's a not found error or validation error
        code = 404 if "not found" in str(e).lower() or "invalid reference" in str(e).lower() else 400
        return jsonify({'error': str(e)}), code
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@exams_bp.route('/time-slots', methods=['GET'])
@swag_from(merge_swagger({
    'tags': ['Academic - Exams'],
    'description': 'Get exam time slots for specific date',
    'parameters': [{
        'name': 'date',
        'in': 'query',
        'type': 'string',
        'format': 'date',
        'required': False,
        'description': 'Date to get slots for (default: today)'
    }],
    'responses': {
        200: {
            'description': 'List of time slots',
            'schema': {
                'type': 'array',
                'items': {'$ref': '#/definitions/TimeSlot'}
            }
        },
        400: {'description': 'Invalid date format'},
        500: {'description': 'Server error'}
    }
}))
def get_exam_time_slots():
    try:
        target_date = None
        if 'date' in request.args:
            target_date = datetime.strptime(request.args['date'], '%Y-%m-%d').date()
        
        slots = service.get_exam_time_slots(target_date)
        return jsonify([{
            'start_time': slot['start_time'].isoformat(),
            'end_time': slot['end_time'].isoformat()
        } for slot in slots]), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Server error', 'details': str(e)}), 500


@exams_bp.route('/dates', methods=['GET'])
@swag_from(merge_swagger({
    'tags': ['Academic - Exams'],
    'description': 'Get all distinct exam dates',
    'responses': {
        200: {
            'description': 'List of exam dates',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'string',
                    'format': 'date'
                }
            }
        },
        500: {'description': 'Server error'}
    }
}))
def get_exam_dates():
    try:
        dates_data = service.get_exam_dates()
        
        #serialized = [item['exam_date'].isoformat() for item in dates_data if item['exam_date']]
        serialized = [{
            'exam_date': item['exam_date'].isoformat() if item['exam_date'] else None
        } for item in dates_data]
        
        return jsonify(serialized), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



 # def serialize_exam(exam):


@exams_bp.route('/<int:exam_id>', methods=['GET'])
@swag_from({
    'tags': ['Academic - Exams'],
    'summary': 'Get exam by ID',
    'description': 'Retrieve a single exam by its exam_id',
    'parameters': [
        {
            'name': 'exam_id',
            'in': 'path',
            'required': True,
            'description': 'ID of the exam to retrieve',
            'schema': {'type': 'integer', 'example': 101}
        }
    ],
    'responses': {
        200: {
            'description': 'Exam details',
            'content': {
                'application/json': {
                    'example': {
                        'exam_id': 1,
                        'course_id': 1,
                        'major_id': 2,
                        'college_id': 3,
                        'level_id': 1,
                        'year_id': 2023,
                        'semester_id': 1,
                        'exam_date': '2023-12-15',
                        'exam_start_time': '09:00:00',
                        'exam_end_time': '11:00:00',
                        'created_at': '2023-10-10T08:00:00'
                    }
                }
            }
        },
        404: {'description': 'Exam not found'},
        500: {'description': 'Server error'}
    }
})
def get_exam_by_id(exam_id):
    try:
        exam = service.get_exam_by_id(exam_id)

        # Convert date/time fields to ISO format
        if 'exam_date' in exam and hasattr(exam['exam_date'], 'isoformat'):
            exam['exam_date'] = exam['exam_date'].isoformat()
        if 'exam_start_time' in exam and hasattr(exam['exam_start_time'], 'isoformat'):
            exam['exam_start_time'] = exam['exam_start_time'].isoformat()
        if 'exam_end_time' in exam and hasattr(exam['exam_end_time'], 'isoformat'):
            exam['exam_end_time'] = exam['exam_end_time'].isoformat()
        if 'created_at' in exam and hasattr(exam['created_at'], 'isoformat'):
            exam['created_at'] = exam['created_at'].isoformat()

        return jsonify(exam), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


#------------------------------------------

@exams_bp.route('/import', methods=['POST'])
@swag_from({
    'tags': ['Academic - Exams'],
    'description': 'Import exams with ALL-OR-NOTHING approach',
    'consumes': ['multipart/form-data'],
    'parameters': [{
        'name': 'file',
        'in': 'formData',
        'type': 'file',
        'required': True,
        'description': 'Excel file (max 10MB) with required columns'
    }],
    'responses': {
        200: {
            'description': 'Import results',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string', 'enum': ['success', 'validation_failed']},
                    'message': {'type': 'string'},
                    'total_records': {'type': 'integer'},
                    'invalid_records': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'row': {'type': 'integer'},
                                'error': {'type': 'string'},
                                'data': {'type': 'object'}
                            }
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Validation error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'},
                    'details': {'type': 'string'}
                }
            }
        },
        500: {
            'description': 'Server error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'},
                    'details': {'type': 'string'}
                }
            }
        }
    }
})

def import_exams():
    if 'file' not in request.files:
        return jsonify({'error': 'File required', 'details': 'No file provided'}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Invalid file', 'details': 'Empty file'}), 400

    try:
# إنشاء كائن جديد وإغلاق أي كائنات سابقة
        file_data = file.read()
        new_file_stream = BytesIO(file_data)
        
        # إغلاق الكائن السابق إذا كان موجوداً (إجراء احترازي)
        if hasattr(file, 'close'):
            file.close()

        result = excel.import_exams_from_excel(new_file_stream, file.filename)
        new_file_stream.close()
    
        if result['status'] == 'validation_failed':
            return jsonify(result), 200
        return jsonify(result), 200
            
    except ValueError as e:
        return jsonify({'error': 'Validation error', 'details': str(e)}), 400
    except RuntimeError as e:
        return jsonify({'error': 'Import failed', 'details': str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'Server error', 'details': str(e)}), 500    

from flask import Blueprint, request, jsonify
from flasgger import swag_from
from services.academic.courses_service import CoursesService

courses_bp = Blueprint('courses', __name__, url_prefix='/api/academic/courses')
service = CoursesService()

SWAGGER_TEMPLATE = {
    'definitions': {
        'Course': {
            'type': 'object',
            'properties': {
                'course_id': {'type': 'integer', 'example': 1},
                'name': {'type': 'string', 'example': 'Introduction to Computer Science'},
                'major_id': {'type': 'integer', 'example': 1},
                'level_id': {'type': 'integer', 'example': 1},
                'year_id': {'type': 'integer', 'example': 1},
                'semester_id': {'type': 'integer', 'example': 1}
            },
            'required': ['name', 'major_id', 'level_id', 'year_id', 'semester_id']
        }
    }
}

def merge_swagger(config):
    return {**config, **SWAGGER_TEMPLATE}

@courses_bp.route('/', methods=['POST'])
@swag_from(merge_swagger({
    'tags': ['Academic - Courses'],
    'description': 'Create new course',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            '$ref': '#/definitions/Course'
        }
    }],
    'responses': {
        201: {'description': 'Created', 'schema': {'$ref': '#/definitions/Course'}},
        400: {'description': 'Validation error'},
        404: {'description': 'Reference not found'},
        409: {'description': 'Course already exists'},
        500: {'description': 'Server error'}
    }
}))
def create_course():
    data = request.get_json()
    try:
        result = service.create_course(
            data['name'],
            data['major_id'],
            data['level_id'],
            data['year_id'],
            data['semester_id']
        )
        return jsonify(result), 201
    except ValueError as e:
        code = 404 if "Invalid reference" in str(e) else 409 if "already exists" in str(e) else 400
        return jsonify({'error': str(e)}), code
    except Exception:
        return jsonify({'error': 'Server error'}), 500

@courses_bp.route('/', methods=['GET'])
@swag_from(merge_swagger({
    'tags': ['Academic - Courses'],
    'description': 'Get all courses',
    'responses': {
        200: {
            'description': 'List of courses',
            'schema': {
                'type': 'array',
                'items': {'$ref': '#/definitions/Course'}
            }
        },
        500: {'description': 'Server error'}
    }
}))
def get_all_courses():
    try:
        courses = service.get_all_courses()
        return jsonify(courses), 200
    except Exception:
        return jsonify({'error': 'Server error'}), 500

@courses_bp.route('/<int:course_id>', methods=['GET'])
@swag_from(merge_swagger({
    'tags': ['Academic - Courses'],
    'description': 'Get course by ID',
    'parameters': [{
        'name': 'course_id',
        'in': 'path',
        'type': 'integer',
        'required': True
    }],
    'responses': {
        200: {'description': 'Course details', 'schema': {'$ref': '#/definitions/Course'}},
        404: {'description': 'Course not found'},
        500: {'description': 'Server error'}
    }
}))
def get_course(course_id):
    try:
        course = service.get_course_by_id(course_id)
        return jsonify(course), 200
    except ValueError:
        return jsonify({'error': 'Course not found'}), 404
    except Exception:
        return jsonify({'error': 'Server error'}), 500

@courses_bp.route('/<int:course_id>', methods=['PUT'])
@swag_from(merge_swagger({
    'tags': ['Academic - Courses'],
    'description': 'Update course',
    'parameters': [
        {
            'name': 'course_id',
            'in': 'path',
            'type': 'integer',
            'required': True
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                '$ref': '#/definitions/Course'
            }
        }
    ],
    'responses': {
        200: {'description': 'Updated course', 'schema': {'$ref': '#/definitions/Course'}},
        400: {'description': 'Validation error'},
        404: {'description': 'Course or reference not found'},
        500: {'description': 'Server error'}
    }
}))
def update_course(course_id):
    data = request.get_json()
    try:
        result = service.update_course(
            course_id,
            data['name'],
            data['major_id'],
            data['level_id'],
            data['year_id'],
            data['semester_id']
        )
        return jsonify(result), 200
    except ValueError as e:
        code = 404 if "not found" in str(e) or "Invalid reference" in str(e) else 400
        return jsonify({'error': str(e)}), code
    except Exception:
        return jsonify({'error': 'Server error'}), 500

@courses_bp.route('/<int:course_id>', methods=['DELETE'])
@swag_from(merge_swagger({
    'tags': ['Academic - Courses'],
    'description': 'Delete course',
    'parameters': [{
        'name': 'course_id',
        'in': 'path',
        'type': 'integer',
        'required': True
    }],
    'responses': {
        200: {
            'description': 'Success message',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'}
                }
            }
        },
        400: {'description': 'Validation error'},
        404: {'description': 'Course not found'},
        500: {'description': 'Server error'}
    }
}))
def delete_course(course_id):
    try:
        result = service.delete_course(course_id)
        return jsonify(result), 200
    except ValueError as e:
        code = 404 if "not found" in str(e) else 400
        return jsonify({'error': str(e)}), code
    except Exception:
        return jsonify({'error': 'Server error'}), 


# Add these new endpoints to the existing controller
@courses_bp.route('/search', methods=['GET'])
@swag_from(merge_swagger({
    'tags': ['Academic - Courses'],
    'description': 'Search courses by name',
    'parameters': [{
        'name': 'q',
        'in': 'query',
        'type': 'string',
        'required': True,
        'description': 'Search term (partial name match)'
    }],
    'responses': {
        200: {
            'description': 'List of matching courses',
            'schema': {
                'type': 'array',
                'items': {'$ref': '#/definitions/Course'}
            }
        },
        400: {'description': 'Invalid search term'},
        500: {'description': 'Server error'}
    }
}))
def search_courses():
    search_term = request.args.get('q')
    try:
        results = service.search_courses(search_term)
        return jsonify(results), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception:
        return jsonify({'error': 'Server error'}), 500

@courses_bp.route('/filter', methods=['GET'])
@swag_from(merge_swagger({
    'tags': ['Academic - Courses'],
    'description': 'Filter courses by criteria',
    'parameters': [
        {
            'name': 'major_id',
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
            'description': 'List of filtered courses',
            'schema': {
                'type': 'array',
                'items': {'$ref': '#/definitions/Course'}
            }
        },
        400: {'description': 'Invalid filter parameters'},
        500: {'description': 'Server error'}
    }
}))
def filter_courses():
    try:
        major_id = request.args.get('major_id', type=int)
        level_id = request.args.get('level_id', type=int)
        year_id = request.args.get('year_id', type=int)
        semester_id = request.args.get('semester_id', type=int)
        
        results = service.filter_courses(
            major_id=major_id,
            level_id=level_id,
            year_id=year_id,
            semester_id=semester_id
        )
        return jsonify(results), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception:
        return jsonify({'error': 'Server error'}), 500
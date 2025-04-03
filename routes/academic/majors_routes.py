from flask import Blueprint, request, jsonify
from flasgger import swag_from
from services.academic.majors_service import MajorsService

majors_bp = Blueprint('majors', __name__, url_prefix='/api/academic/majors')
service = MajorsService()

# تعريف نموذج Major لاستخدامه في جميع الدوال
SWAGGER_TEMPLATE = {
    'definitions': {
        'Major': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer', 'example': 1},
                'name': {'type': 'string', 'example': 'Computer Science'},
                'college_id': {'type': 'integer', 'example': 1},
                'created_at': {'type': 'string', 'format': 'date-time'},
                'updated_at': {'type': 'string', 'format': 'date-time'}
            }
        }
    }
}

def merge_swagger(config):
    """دمج تكوين Swagger مع التعريفات الأساسية"""
    return {**config, **SWAGGER_TEMPLATE}

@majors_bp.route('/', methods=['POST'])
@swag_from(merge_swagger({
    'tags': ['Academic - Majors'],
    'description': 'Create new major',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string', 'example': 'Computer Science'},
                'college_id': {'type': 'integer', 'example': 1}
            },
            'required': ['name', 'college_id']
        }
    }],
    'responses': {
        201: {'description': 'Major created', 'schema': {'$ref': '#/definitions/Major'}},
        400: {'description': 'Validation error'},
        404: {'description': 'College not found'},
        409: {'description': 'Major exists'},
        500: {'description': 'Server error'}
    }
}))
def create_major():
    try:
        data = request.get_json()
        major = service.create_major(data['name'], data['college_id'])
        return jsonify(major), 201
    except ValueError as e:
        code = 404 if "College does not exist" in str(e) else 409 if "already exists" in str(e) else 400
        return jsonify({'error': str(e)}), code
    except Exception:
        return jsonify({'error': 'Server error'}), 500

@majors_bp.route('/college/<int:college_id>', methods=['GET'])
@swag_from(merge_swagger({
    'tags': ['Academic - Majors'],
    'description': 'Get majors by college',
    'parameters': [{
        'name': 'college_id',
        'in': 'path',
        'type': 'integer',
        'required': True
    }],
    'responses': {
        200: {
            'description': 'Majors list', 
            'schema': {
                'type': 'array', 
                'items': {'$ref': '#/definitions/Major'}
            }
        },
        404: {'description': 'College not found'},
        500: {'description': 'Server error'}
    }
}))
def get_majors_by_college(college_id):
    try:
        majors = service.get_majors_by_college(college_id)
        return jsonify(majors), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception:
        return jsonify({'error': 'Server error'}), 500

@majors_bp.route('/<int:major_id>', methods=['GET'])
@swag_from(merge_swagger({
    'tags': ['Academic - Majors'],
    'description': 'Get major details by ID',
    'parameters': [{
        'name': 'major_id',
        'in': 'path',
        'type': 'integer',
        'required': True,
        'description': 'ID of the major to retrieve'
    }],
    'responses': {
        200: {
            'description': 'Major details',
            'schema': {'$ref': '#/definitions/Major'}
        },
        404: {'description': 'Major not found'},
        500: {'description': 'Server error'}
    }
}))
def get_major(major_id):
    try:
        major = service.get_major(major_id)
        return jsonify(major), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception:
        return jsonify({'error': 'Server error'}), 500

@majors_bp.route('/<int:major_id>', methods=['PUT'])
@swag_from(merge_swagger({
    'tags': ['Academic - Majors'],
    'description': 'Update major information',
    'parameters': [
        {
            'name': 'major_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the major to update'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'example': 'Updated Major Name'},
                    'college_id': {'type': 'integer', 'example': 1}
                },
                'required': ['name', 'college_id']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Updated major',
            'schema': {'$ref': '#/definitions/Major'}
        },
        400: {'description': 'Validation error'},
        404: {'description': 'Major or College not found'},
        409: {'description': 'Major name already exists'},
        500: {'description': 'Server error'}
    }
}))
def update_major(major_id):
    try:
        data = request.get_json()
        major = service.update_major(
            major_id=major_id,
            name=data['name'],
            college_id=data['college_id']
        )
        return jsonify(major), 200
    except ValueError as e:
        code = 404 if "not found" in str(e) else 409 if "already exists" in str(e) else 400
        return jsonify({'error': str(e)}), code
    except Exception:
        return jsonify({'error': 'Server error'}), 500

@majors_bp.route('/<int:major_id>', methods=['DELETE'])
@swag_from(merge_swagger({
    'tags': ['Academic - Majors'],
    'description': 'Delete a major',
    'parameters': [{
        'name': 'major_id',
        'in': 'path',
        'type': 'integer',
        'required': True,
        'description': 'ID of the major to delete'
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
        404: {'description': 'Major not found'},
        500: {'description': 'Server error'}
    }
}))
def delete_major(major_id):
    try:
        result = service.delete_major(major_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception:
        return jsonify({'error': 'Server error'}), 500
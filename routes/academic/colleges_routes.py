# routes/academic/colleges_routes.py
from flask import Blueprint, request, jsonify
from flasgger import swag_from
from services.academic.colleges_service import CollegesService

colleges_bp = Blueprint('colleges', __name__, url_prefix='/api/academic/colleges')
service = CollegesService()

@colleges_bp.route('/', methods=['POST'])
@swag_from({
    'tags':  ['Academic/Colleges'],
    'description': 'Create new college',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string', 'example': 'College of Science'}
            },
            'required': ['name']
        }
    }],
    'responses': {
        201: {'description': 'College created', 'schema': {'$ref': '#/definitions/College'}},
        400: {'description': 'Validation error'},
        409: {'description': 'College exists'},
        500: {'description': 'Server error'}
    }
})
def create_college():
    try:
        data = request.get_json()
        college = service.create_college(data['name'])
        return jsonify(college), 201
    except ValueError as e:
        code = 409 if "already exists" in str(e) else 400
        return jsonify({'error': str(e)}), code
    except Exception:
        return jsonify({'error': 'Server error'}), 500

@colleges_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['Academic/Colleges'],
    'description': 'List all colleges',
    'responses': {
        200: {'description': 'Colleges list', 'schema': {'type': 'array', 'items': {'$ref': '#/definitions/College'}}},
        500: {'description': 'Server error'}
    }
})
def get_colleges():
    try:
        colleges = service.get_all_colleges()
        return jsonify(colleges), 200
    except Exception:
        return jsonify({'error': 'Server error'}), 500


# routes/academic/colleges_routes.py (continued)

@colleges_bp.route('/<int:college_id>', methods=['GET'])
@swag_from({
    'tags':  ['Academic/Colleges'],
    'description': 'Get college by ID',
    'parameters': [{
        'name': 'college_id',
        'in': 'path',
        'type': 'integer',
        'required': True,
        'description': 'ID of the college to retrieve'
    }],
    'responses': {
        200: {
            'description': 'College details',
            'schema': {'$ref': '#/definitions/College'}
        },
        404: {'description': 'College not found'},
        500: {'description': 'Server error'}
    }
})
def get_college(college_id):
    try:
        college = service.get_college(college_id)
        return jsonify(college), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception:
        return jsonify({'error': 'Server error'}), 500

@colleges_bp.route('/<int:college_id>', methods=['PUT'])
@swag_from({
    'tags': ['Academic/Colleges'],
    'description': 'Update college name',
    'parameters': [
        {
            'name': 'college_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the college to update'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {
                        'type': 'string',
                        'example': 'Updated College Name'
                    }
                },
                'required': ['name']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Updated college',
            'schema': {'$ref': '#/definitions/College'}
        },
        400: {'description': 'Validation error'},
        404: {'description': 'College not found'},
        409: {'description': 'College name already exists'},
        500: {'description': 'Server error'}
    }
})
def update_college(college_id):
    try:
        data = request.get_json()
        college = service.update_college(college_id, data['name'])
        return jsonify(college), 200
    except ValueError as e:
        code = 409 if "already exists" in str(e) else 404 if "not found" in str(e) else 400
        return jsonify({'error': str(e)}), code
    except Exception:
        return jsonify({'error': 'Server error'}), 500

@colleges_bp.route('/<int:college_id>', methods=['DELETE'])
@swag_from({
    'tags':  ['Academic/Colleges'],
    'description': 'Delete a college',
    'parameters': [{
        'name': 'college_id',
        'in': 'path',
        'type': 'integer',
        'required': True,
        'description': 'ID of the college to delete'
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
        404: {'description': 'College not found'},
        500: {'description': 'Server error'}
    }
})
def delete_college(college_id):
    try:
        result = service.delete_college(college_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception:
        return jsonify({'error': 'Server error'}), 500
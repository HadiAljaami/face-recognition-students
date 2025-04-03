from flask import Blueprint, request, jsonify
from flasgger import swag_from
from services.academic.semesters_service import SemestersService

semesters_bp = Blueprint('semesters', __name__, url_prefix='/api/academic/semesters')
service = SemestersService()

SWAGGER_TEMPLATE = {
    'definitions': {
        'Semester': {
            'type': 'object',
            'properties': {
                'semester_id': {'type': 'integer', 'example': 1},
                'semester_name': {'type': 'string', 'example': 'Fall 2023'}
            }
        }
    }
}

def merge_swagger(config):
    return {**config, **SWAGGER_TEMPLATE}

@semesters_bp.route('/', methods=['POST'])
@swag_from(merge_swagger({
    'tags': ['Academic - Semesters'],
    'description': 'Create new semester',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'semester_name': {'type': 'string', 'example': 'Fall 2023'}
            },
            'required': ['semester_name']
        }
    }],
    'responses': {
        201: {'description': 'Created', 'schema': {'$ref': '#/definitions/Semester'}},
        400: {'description': 'Validation error'},
        409: {'description': 'Semester exists'},
        500: {'description': 'Server error'}
    }
}))
def create_semester():
    data = request.get_json()
    try:
        result = service.create_semester(data['semester_name'])
        return jsonify(result), 201
    except ValueError as e:
        code = 409 if "already exists" in str(e) else 400
        return jsonify({'error': str(e)}), code
    except Exception:
        return jsonify({'error': 'Server error'}), 500

@semesters_bp.route('/', methods=['GET'])
@swag_from(merge_swagger({
    'tags': ['Academic - Semesters'],
    'description': 'Get all semesters',
    'responses': {
        200: {
            'description': 'List of semesters',
            'schema': {
                'type': 'array',
                'items': {'$ref': '#/definitions/Semester'}
            }
        },
        500: {'description': 'Server error'}
    }
}))
def get_all_semesters():
    try:
        semesters = service.get_all_semesters()
        return jsonify(semesters), 200
    except Exception:
        return jsonify({'error': 'Server error'}), 500

@semesters_bp.route('/<int:semester_id>', methods=['GET'])
@swag_from(merge_swagger({
    'tags': ['Academic - Semesters'],
    'description': 'Get semester by ID',
    'parameters': [{
        'name': 'semester_id',
        'in': 'path',
        'type': 'integer',
        'required': True
    }],
    'responses': {
        200: {'description': 'Semester details', 'schema': {'$ref': '#/definitions/Semester'}},
        404: {'description': 'Semester not found'},
        500: {'description': 'Server error'}
    }
}))
def get_semester(semester_id):
    try:
        semester = service.get_semester_by_id(semester_id)
        return jsonify(semester), 200
    except ValueError:
        return jsonify({'error': 'Semester not found'}), 404
    except Exception:
        return jsonify({'error': 'Server error'}), 500

@semesters_bp.route('/<int:semester_id>', methods=['PUT'])
@swag_from(merge_swagger({
    'tags': ['Academic - Semesters'],
    'description': 'Update semester',
    'parameters': [
        {
            'name': 'semester_id',
            'in': 'path',
            'type': 'integer',
            'required': True
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'semester_name': {'type': 'string', 'example': 'Fall 2023 Updated'}
                },
                'required': ['semester_name']
            }
        }
    ],
    'responses': {
        200: {'description': 'Updated semester', 'schema': {'$ref': '#/definitions/Semester'}},
        400: {'description': 'Validation error'},
        404: {'description': 'Semester not found'},
        409: {'description': 'Semester name exists'},
        500: {'description': 'Server error'}
    }
}))
def update_semester(semester_id):
    data = request.get_json()
    try:
        result = service.update_semester(semester_id, data['semester_name'])
        return jsonify(result), 200
    except ValueError as e:
        code = 409 if "already exists" in str(e) else 404 if "not found" in str(e) else 400
        return jsonify({'error': str(e)}), code
    except Exception:
        return jsonify({'error': 'Server error'}), 500

@semesters_bp.route('/<int:semester_id>', methods=['DELETE'])
@swag_from(merge_swagger({
    'tags': ['Academic - Semesters'],
    'description': 'Delete semester',
    'parameters': [{
        'name': 'semester_id',
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
        404: {'description': 'Semester not found'},
        500: {'description': 'Server error'}
    }
}))
def delete_semester(semester_id):
    try:
        result = service.delete_semester(semester_id)
        return jsonify(result), 200
    except ValueError as e:
        code = 404 if "not found" in str(e) else 400
        return jsonify({'error': str(e)}), code
    except Exception:
        return jsonify({'error': 'Server error'}), 500
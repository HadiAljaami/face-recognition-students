from flask import Blueprint, request, jsonify
from flasgger import swag_from
from services.academic.academic_years_service import AcademicYearsService

years_bp = Blueprint('academic_years', __name__, url_prefix='/api/academic/years')
service = AcademicYearsService()

SWAGGER_TEMPLATE = {
    'definitions': {
        'AcademicYear': {
            'type': 'object',
            'properties': {
                'year_id': {'type': 'integer', 'example': 1},
                'year_name': {'type': 'string', 'example': '2023-2024'}
            }
        }
    }
}

def merge_swagger(config):
    return {**config, **SWAGGER_TEMPLATE}

@years_bp.route('/', methods=['POST'])
@swag_from(merge_swagger({
    'tags': ['Academic Years'],
    'description': 'Create new academic year',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'year_name': {'type': 'string', 'example': '2023-2024'}
            },
            'required': ['year_name']
        }
    }],
    'responses': {
        201: {'description': 'Created', 'schema': {'$ref': '#/definitions/AcademicYear'}},
        400: {'description': 'Validation error'},
        409: {'description': 'Year already exists'},
        500: {'description': 'Internal server error'},
        503: {'description': 'Service unavailable'}
    }
}))
def create_year():
    data = request.get_json()
    try:
        result = service.create_year(data.get('year_name'))
        return jsonify(result), 201
    except ValueError as e:
        code = 409 if "already exists" in str(e) else 400
        return jsonify({'error': str(e)}), code
    except RuntimeError:
        return jsonify({'error': 'Service unavailable'}), 503
    except Exception:
        return jsonify({'error': 'Internal server error'}), 500

@years_bp.route('/', methods=['GET'])
@swag_from(merge_swagger({
    'tags': ['Academic Years'],
    'description': 'Get all academic years',
    'responses': {
        200: {
            'description': 'List of years',
            'schema': {
                'type': 'array',
                'items': {'$ref': '#/definitions/AcademicYear'}
            }
        },
        500: {'description': 'Internal server error'},
        503: {'description': 'Service unavailable'}
    }
}))
def get_all_years():
    try:
        years = service.get_all_years()
        return jsonify(years), 200
    except RuntimeError:
        return jsonify({'error': 'Service unavailable'}), 503
    except Exception:
        return jsonify({'error': 'Internal server error'}), 500

@years_bp.route('/<int:year_id>', methods=['GET'])
@swag_from(merge_swagger({
    'tags': ['Academic Years'],
    'description': 'Get academic year by ID',
    'parameters': [{
        'name': 'year_id',
        'in': 'path',
        'type': 'integer',
        'required': True
    }],
    'responses': {
        200: {'description': 'Year details', 'schema': {'$ref': '#/definitions/AcademicYear'}},
        404: {'description': 'Year not found'},
        500: {'description': 'Internal server error'},
        503: {'description': 'Service unavailable'}
    }
}))
def get_year(year_id):
    try:
        year = service.get_year_by_id(year_id)
        return jsonify(year), 200
    except ValueError:
        return jsonify({'error': 'Academic year not found'}), 404
    except RuntimeError:
        return jsonify({'error': 'Service unavailable'}), 503
    except Exception:
        return jsonify({'error': 'Internal server error'}), 500

@years_bp.route('/<int:year_id>', methods=['PUT'])
@swag_from(merge_swagger({
    'tags': ['Academic Years'],
    'description': 'Update academic year',
    'parameters': [
        {
            'name': 'year_id',
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
                    'year_name': {'type': 'string', 'example': '2023-2024'}
                },
                'required': ['year_name']
            }
        }
    ],
    'responses': {
        200: {'description': 'Updated year', 'schema': {'$ref': '#/definitions/AcademicYear'}},
        400: {'description': 'Validation error'},
        404: {'description': 'Year not found'},
        409: {'description': 'Year name exists'},
        500: {'description': 'Internal server error'},
        503: {'description': 'Service unavailable'}
    }
}))
def update_year(year_id):
    data = request.get_json()
    try:
        result = service.update_year(year_id, data.get('year_name'))
        return jsonify(result), 200
    except ValueError as e:
        code = 409 if "already exists" in str(e) else 404 if "not found" in str(e) else 400
        return jsonify({'error': str(e)}), code
    except RuntimeError:
        return jsonify({'error': 'Service unavailable'}), 503
    except Exception:
        return jsonify({'error': 'Internal server error'}), 500

@years_bp.route('/<int:year_id>', methods=['DELETE'])
@swag_from(merge_swagger({
    'tags': ['Academic Years'],
    'description': 'Delete academic year',
    'parameters': [{
        'name': 'year_id',
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
        404: {'description': 'Year not found'},
        500: {'description': 'Internal server error'},
        503: {'description': 'Service unavailable'}
    }
}))
def delete_year(year_id):
    try:
        result = service.delete_year(year_id)
        return jsonify(result), 200
    except ValueError as e:
        code = 404 if "not found" in str(e) else 400
        return jsonify({'error': str(e)}), code
    except RuntimeError:
        return jsonify({'error': 'Service unavailable'}), 503
    except Exception:
        return jsonify({'error': 'Internal server error'}), 500
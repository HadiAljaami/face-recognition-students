from flask import Blueprint, request, jsonify
from flasgger import swag_from
from services.academic.levels_service import LevelsService

levels_bp = Blueprint('levels', __name__, url_prefix='/api/academic/levels')
service = LevelsService()

# تعريف نموذج Level لاستخدامه في جميع الدوال
SWAGGER_TEMPLATE = {
    'definitions': {
        'Level': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer', 'example': 1},
                'level_name': {'type': 'string', 'example': 'First Year'},
                'created_at': {'type': 'string', 'format': 'date-time'},
                'updated_at': {'type': 'string', 'format': 'date-time'}
            }
        }
    }
}

def merge_swagger(config):
    """دمج تكوين Swagger مع التعريفات الأساسية"""
    return {**config, **SWAGGER_TEMPLATE}

@levels_bp.route('/', methods=['POST'])
@swag_from(merge_swagger({
    'tags': ['Academic - Levels'],
    'description': 'Create new level',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'level_name': {'type': 'string', 'example': 'First Year'}
            },
            'required': ['level_name']
        }
    }],
    'responses': {
        201: {'description': 'Level created', 'schema': {'$ref': '#/definitions/Level'}},
        400: {'description': 'Validation error'},
        409: {'description': 'Level exists'},
        500: {'description': 'Server error'},
        503: {'description': 'Service unavailable'}
    }
}))
def create_level():
    try:
        data = request.get_json()
        level = service.create_level(data['level_name'])
        return jsonify(level), 201
    except ValueError as e:
        code = 409 if "already exists" in str(e) else 400
        return jsonify({'error': str(e)}), code
    except RuntimeError:
        return jsonify({'error': 'Service unavailable'}), 503
    except Exception:
        return jsonify({'error': 'Internal server error'}), 500

@levels_bp.route('/', methods=['GET'])
@swag_from(merge_swagger({
    'tags': ['Academic - Levels'],
    'description': 'Get all levels',
    'responses': {
        200: {
            'description': 'List of levels',
            'schema': {
                'type': 'array',
                'items': {'$ref': '#/definitions/Level'}
            }
        },
        503: {'description': 'Service unavailable'},
        500: {'description': 'Server error'}
    }
}))
def get_levels():
    try:
        levels = service.get_all_levels()
        return jsonify(levels), 200
    except RuntimeError:
        return jsonify({'error': 'Service unavailable'}), 503
    except Exception:
        return jsonify({'error': 'Internal server error'}), 500

@levels_bp.route('/<int:level_id>', methods=['GET'])
@swag_from(merge_swagger({
    'tags': ['Academic - Levels'],
    'description': 'Get level by ID',
    'parameters': [{
        'name': 'level_id',
        'in': 'path',
        'type': 'integer',
        'required': True
    }],
    'responses': {
        200: {'description': 'Level details', 'schema': {'$ref': '#/definitions/Level'}},
        404: {'description': 'Level not found'},
        503: {'description': 'Service unavailable'},
        500: {'description': 'Server error'}
    }
}))
def get_level(level_id):
    try:
        level = service.get_level(level_id)
        return jsonify(level), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except RuntimeError:
        return jsonify({'error': 'Service unavailable'}), 503
    except Exception:
        return jsonify({'error': 'Internal server error'}), 500

@levels_bp.route('/<int:level_id>', methods=['PUT'])
@swag_from(merge_swagger({
    'tags': ['Academic - Levels'],
    'description': 'Update level',
    'parameters': [
        {
            'name': 'level_id',
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
                    'level_name': {'type': 'string', 'example': 'Updated Level Name'}
                },
                'required': ['level_name']
            }
        }
    ],
    'responses': {
        200: {'description': 'Updated level', 'schema': {'$ref': '#/definitions/Level'}},
        400: {'description': 'Validation error'},
        404: {'description': 'Level not found'},
        409: {'description': 'Level name already exists'},
        503: {'description': 'Service unavailable'},
        500: {'description': 'Server error'}
    }
}))
def update_level(level_id):
    try:
        data = request.get_json()
        level = service.update_level(level_id, data['level_name'])
        return jsonify(level), 200
    except ValueError as e:
        code = 409 if "already exists" in str(e) else 404 if "not found" in str(e) else 400
        return jsonify({'error': str(e)}), code
    except RuntimeError:
        return jsonify({'error': 'Service unavailable'}), 503
    except Exception:
        return jsonify({'error': 'Internal server error'}), 500

@levels_bp.route('/<int:level_id>', methods=['DELETE'])
@swag_from(merge_swagger({
    'tags': ['Academic - Levels'],
    'description': 'Delete level',
    'parameters': [{
        'name': 'level_id',
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
                    'message': {'type': 'string'},
                    'deleted_id': {'type': 'integer'}
                }
            }
        },
        404: {'description': 'Level not found'},
        503: {'description': 'Service unavailable'},
        500: {'description': 'Server error'}
    }
}))
def delete_level(level_id):
    try:
        deleted_id = service.delete_level(level_id)
        return jsonify({
            'message': 'Level deleted successfully',
            'deleted_id': deleted_id
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except RuntimeError:
        return jsonify({'error': 'Service unavailable'}), 503
    except Exception:
        return jsonify({'error': 'Internal server error'}), 500
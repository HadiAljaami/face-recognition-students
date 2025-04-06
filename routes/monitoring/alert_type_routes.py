from flask import Blueprint, request, jsonify
from flasgger import swag_from
from services.monitoring.alert_type_service import AlertTypeService

alert_type_bp = Blueprint('alert_types', __name__, url_prefix='/api/alert-types')
service = AlertTypeService()

def handle_error(e, status_code):
    """Helper function for error handling"""
    error_message = str(e)
    if "database" in error_message.lower():
        return jsonify({"error": "Database operation failed"}), 500
    return jsonify({"error": error_message}), status_code

@alert_type_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['Alert Types'],
    'description': 'Create a new alert type',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'type_name': {
                        'type': 'string',
                        'example': 'Cheating Attempt',
                        'description': 'Name of the alert type'
                    }
                },
                'required': ['type_name']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Alert type created successfully',
            'examples': {
                'application/json': {
                    'id': 1,
                    'type_name': 'Cheating Attempt'
                }
            }
        },
        400: {
            'description': 'Validation error',
            'examples': {
                'application/json': {
                    'error': 'Type name must be at least 2 characters'
                }
            }
        },
        500: {
            'description': 'Internal server error',
            'examples': {
                'application/json': {
                    'error': 'Database operation failed'
                }
            }
        }
    }
})
def create_alert_type():
    """
    Create a new alert type
    """
    data = request.get_json()
    try:
        alert_type = service.create_alert_type(data.get('type_name'))
        return jsonify(alert_type), 201
    except ValueError as e:
        return handle_error(e, 400)
    except Exception as e:
        return handle_error(e, 500)

@alert_type_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['Alert Types'],
    'description': 'Get all alert types',
    'responses': {
        200: {
            'description': 'List of all alert types',
            'examples': {
                'application/json': [
                    {
                        'id': 1,
                        'type_name': 'Cheating Attempt'
                    },
                    {
                        'id': 2,
                        'type_name': 'Unauthorized Device'
                    }
                ]
            }
        },
        500: {
            'description': 'Internal server error'
        }
    }
})
def list_alert_types():
    """
    Get all alert types
    """
    try:
        alert_types = service.get_all_alert_types()
        return jsonify(alert_types)
    except Exception as e:
        return handle_error(e, 500)

@alert_type_bp.route('/<int:type_id>', methods=['GET'])
@swag_from({
    'tags': ['Alert Types'],
    'description': 'Get specific alert type by ID',
    'parameters': [
        {
            'name': 'type_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the alert type'
        }
    ],
    'responses': {
        200: {
            'description': 'Alert type details',
            'examples': {
                'application/json': {
                    'id': 1,
                    'type_name': 'Cheating Attempt'
                }
            }
        },
        404: {
            'description': 'Alert type not found'
        },
        500: {
            'description': 'Internal server error'
        }
    }
})
def get_alert_type(type_id):
    """
    Get alert type by ID
    """
    try:
        alert_type = service.get_alert_type(type_id)
        if not alert_type:
            return jsonify({"error": "Alert type not found"}), 404
        return jsonify(alert_type)
    except Exception as e:
        return handle_error(e, 500)

@alert_type_bp.route('/<int:type_id>', methods=['PUT'])
@swag_from({
    'tags': ['Alert Types'],
    'description': 'Update an existing alert type',
    'parameters': [
        {
            'name': 'type_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the alert type to update'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'type_name': {
                        'type': 'string',
                        'example': 'New Type Name',
                        'description': 'New name for the alert type'
                    }
                },
                'required': ['type_name']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Updated alert type',
            'examples': {
                'application/json': {
                    'id': 1,
                    'type_name': 'New Type Name'
                }
            }
        },
        400: {
            'description': 'Validation error'
        },
        404: {
            'description': 'Alert type not found'
        },
        500: {
            'description': 'Internal server error'
        }
    }
})
def update_alert_type(type_id):
    """
    Update alert type
    """
    data = request.get_json()
    try:
        alert_type = service.update_alert_type(type_id, data.get('type_name'))
        return jsonify(alert_type)
    except ValueError as e:
        return handle_error(e, 400)
    except Exception as e:
        return handle_error(e, 500)

@alert_type_bp.route('/<int:type_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Alert Types'],
    'description': 'Delete an alert type',
    'parameters': [
        {
            'name': 'type_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the alert type to delete'
        }
    ],
    'responses': {
        200: {
            'description': 'Success message',
            'examples': {
                'application/json': {
                    'message': 'Alert type deleted successfully'
                }
            }
        },
        400: {
            'description': 'Cannot delete (type is in use)'
        },
        404: {
            'description': 'Alert type not found'
        },
        500: {
            'description': 'Internal server error'
        }
    }
})
def delete_alert_type(type_id):
    """
    Delete alert type
    """
    try:
        success = service.delete_alert_type(type_id)
        if not success:
            return jsonify({"error": "Alert type not found"}), 404
        return jsonify({"message": "Alert type deleted successfully"})
    except ValueError as e:
        return handle_error(e, 400)
    except Exception as e:
        return handle_error(e, 500)
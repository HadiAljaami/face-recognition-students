# routes/devices_routes.py
from flask import Blueprint, request, jsonify
from services.devices_service import DevicesService
from database.devices_repository import DevicesRepository
from flasgger import swag_from

devices_bp = Blueprint('devices', __name__) #, url_prefix='/api/devices'
repository = DevicesRepository()
service = DevicesService(repository)

@devices_bp.route('/api/devices/register', methods=['POST'])
@swag_from({
    'tags': ['Devices'],
    'description': 'Register a new device',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'device_number': {'type': 'integer', 'example': 123},
                    'room_number': {'type': 'string', 'example': 'A101'},
                    'center_id': {'type': 'integer', 'example': 1}
                },
                'required': ['device_number', 'room_number', 'center_id']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Device registered successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'device': {'type': 'object'}
                }
            }
        },
        400: {'description': 'Invalid input'},
        500: {'description': 'Internal server error'}
    }
})
def register_device():
    """تسجيل جهاز جديد"""
    try:
        data = request.get_json()
        device = service.register_device(
            device_number=data['device_number'],
            room_number=data['room_number'],
            center_id=data['center_id']
        )
        return jsonify({
            'message': 'Device registered successfully',
            'device': device,
            'token': device['device_token']  # إرجاع التوكن للجهاز
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@devices_bp.route('/api/devices/index', methods=['GET'])
@swag_from({
    'tags': ['Devices'],
    'description': 'Get all devices with optional filtering',
    'parameters': [
        {
            'name': 'center_id',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'Filter by center ID'
        },
        {
            'name': 'room_number',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Filter by room number'
        }
    ],
    'responses': {
        200: {
            'description': 'List of devices',
            'schema': {
                'type': 'object',
                'properties': {
                    'devices': {
                        'type': 'array',
                        'items': {'type': 'object'}
                    }
                }
            }
        },
        500: {'description': 'Internal server error'}
    }
})
def get_devices():
    """الحصول على جميع الأجهزة مع فلترة اختيارية"""
    try:
        center_id = request.args.get('center_id', type=int)
        room_number = request.args.get('room_number')
        
        filters = {}
        if center_id is not None:
            filters['center_id'] = center_id
        if room_number:
            filters['room_number'] = room_number
            
        devices = service.get_all_devices(filters)
        return jsonify({'devices': devices}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@devices_bp.route('/api/devices/update/<int:device_id>', methods=['PUT'])
@swag_from({
    'tags': ['Devices'],
    'description': 'Update device information',
    'parameters': [
        {
            'name': 'device_id',
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
                    'device_number': {'type': 'integer', 'example': 123},
                    'room_number': {'type': 'string', 'example': 'A101'},
                    'center_id': {'type': 'integer', 'example': 1}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Device updated successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'device': {'type': 'object'}
                }
            }
        },
        404: {'description': 'Device not found'},
        500: {'description': 'Internal server error'}
    }
})
def update_device(device_id):
    """تحديث بيانات الجهاز"""
    try:
        data = request.get_json()
        if service.update_device(device_id, **data):
            device = service.get_device_by_number(data.get('device_number')) or \
                    service.repository.get_device_by_id(device_id)
            return jsonify({
                'message': 'Device updated successfully',
                'device': device
            }), 200
        return jsonify({'error': 'Device not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@devices_bp.route('/api/devices/toggle/<int:device_id>/status', methods=['PATCH'])
@swag_from({
    'tags': ['Devices'],
    'description': 'Toggle device status',
    'parameters': [
        {
            'name': 'device_id',
            'in': 'path',
            'type': 'integer',
            'required': True
        }
    ],
    'responses': {
        200: {
            'description': 'Device status toggled successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'new_status': {'type': 'integer'}
                }
            }
        },
        404: {'description': 'Device not found'},
        500: {'description': 'Internal server error'}
    }
})
def toggle_device_status(device_id):
    """تبديل حالة الجهاز (تشغيل/إيقاف)"""
    try:
        device = service.toggle_device_status(device_id)
        if device:
            return jsonify({
                'message': 'Device status toggled successfully',
                'new_status': device['status']
            }), 200
        return jsonify({'error': 'Device not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@devices_bp.route('/api/devices/update-token/<int:device_id>/token', methods=['PATCH'])
@swag_from({
    'tags': ['Devices'],
    'description': 'Refresh device token',
    'parameters': [
        {
            'name': 'device_id',
            'in': 'path',
            'type': 'integer',
            'required': True
        }
    ],
    'responses': {
        200: {
            'description': 'Token refreshed successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'new_token': {'type': 'string'}
                }
            }
        },
        404: {'description': 'Device not found'},
        500: {'description': 'Internal server error'}
    }
})
def refresh_device_token(device_id):
    """تحديث توكن الجهاز"""
    try:
        new_token = service.refresh_device_token(device_id)
        if new_token:
            return jsonify({
                'message': 'Token refreshed successfully',
                'new_token': new_token
            }), 200
        return jsonify({'error': 'Device not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@devices_bp.route('/api/devices/validate-token', methods=['POST'])
@swag_from({
    'tags': ['Devices'],
    'description': 'Validate device token',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'token': {'type': 'string'}
                },
                'required': ['token']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Token validation result',
            'schema': {
                'type': 'object',
                'properties': {
                    'valid': {'type': 'boolean'},
                    'device': {'type': 'object'}
                }
            }
        },
        500: {'description': 'Internal server error'}
    }
})
def validate_token():
    """التحقق من صحة توكن الجهاز"""
    try:
        token = request.json.get('token')
        device = service.repository.get_device_by_token(token)
        if device and device['status'] == 1:
            return jsonify({
                'valid': True,
                'device': device
            }), 200
        return jsonify({'valid': False}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@devices_bp.route('/api/devices/show', methods=['GET'])
@swag_from({
    'tags': ['Devices'],
    'description': 'Get device by ID or device number',
    'parameters': [
        {
            'name': 'device_id',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'Device ID'
        },
        {
            'name': 'device_number',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'Device number'
        }
    ],
    'responses': {
        200: {
            'description': 'Device details',
            'schema': {
                'type': 'object',
                'properties': {
                    'device': {'type': 'object'}
                }
            }
        },
        400: {'description': 'Missing or invalid parameters'},
        404: {'description': 'Device not found'},
        500: {'description': 'Internal server error'}
    }
})
def get_device():
    """جلب بيانات جهاز باستخدام id أو رقم الجهاز"""
    try:
        device_id = request.args.get('device_id', type=int)
        device_number = request.args.get('device_number', type=int)

        if not device_id and not device_number:
            return jsonify({'error': 'يرجى توفير device_id أو device_number'}), 400

        device = None
        if device_id:
            device = service.repository.get_device_by_id(device_id)
        elif device_number:
            device = service.get_device_by_number(device_number)

        if device:
            return jsonify({'device': device}), 200
        else:
            return jsonify({'error': 'Device not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

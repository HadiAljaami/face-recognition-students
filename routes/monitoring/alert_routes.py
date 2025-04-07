from flask import Blueprint, request, jsonify
from flasgger import swag_from
from services.monitoring.alert_service import AlertService
from datetime import datetime
alert_bp = Blueprint('alerts', __name__, url_prefix='/api/alerts')
service = AlertService()

@alert_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['Alerts'],
    'description': 'Create a new alert',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'exam_id': {'type': 'integer', 'example': 1},
                'student_id': {'type': 'integer', 'example': 1001},
                'device_id': {'type': 'integer', 'example': 5},
                'alert_type': {'type': 'integer', 'example': 1},
                'message': {'type': 'string', 'example': 'Student using phone'}
            },
            'required': ['exam_id', 'student_id', 'device_id', 'alert_type']
        }
    }],
    'responses': {
        201: {
            'description': 'Alert created',
            'examples': {
                'application/json': {
                    'alert_id': 1,
                    'exam_id': 1,
                    'student_id': 1001,
                    'device_id': 5,
                    'alert_type': 1,
                    'alert_message': 'Student using phone',
                    'is_read': False
                }
            }
        },
        400: {'description': 'Invalid input'},
        500: {'description': 'Server error'}
    }
})
def create_alert():
    data = request.get_json()
    try:
        alert = service.create_alert(
            exam_id=data.get('exam_id'),
            student_id=data.get('student_id'),
            device_id=data.get('device_id'),
            alert_type=data.get('alert_type'),
            message=data.get('message')
        )
        return jsonify(alert), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@alert_bp.route('/devices', methods=['GET'])
@swag_from({
    'tags': ['Alerts'],
    'description': 'Get devices with cheating alerts',
    'parameters': [
        {
            'name': 'center_id',
            'in': 'query',
            'type': 'integer',
            'required': False
        },
        {
            'name': 'room_number',
            'in': 'query',
            'type': 'string',
            'required': False
        },
        {
            'name': 'exam_date',
            'in': 'query',
            'type': 'string',
            'format': 'date',
            'required': False
        },
        {
            'name': 'start_time',
            'in': 'query',
            'type': 'string',
            'format': 'time',
            'description': 'Format: HH:MM:SS',
            'required': False
        },
        {
            'name': 'end_time',
            'in': 'query',
            'type': 'string',
            'format': 'time',
            'description': 'Format: HH:MM:SS',
            'required': False
        }
    ],
    'responses': {
        200: {
            'description': 'List of devices with alerts',
            'examples': {
                'application/json': [{
                    'device_id': 1,
                    'device_number': 101,
                    'room_number': 'A1',
                    'center_name': 'Main Center',
                    'status': 1,
                    'alert_count': 3,
                    'unread_count':2,
                    'last_alert_time': '2023-05-15T10:30:00',
                    'student_id': 1001,
                    'exam_id': 5,
                    'exam_date': '2023-05-15',
                    'exam_period': '09:00 - 11:00'
                }]
            }
        },
        500: {'description': 'Server error'}
    }
})
def get_alert_devices():
    try:
        # معالجة المدخلات
        center_id = request.args.get('center_id', type=int)
        room_number = request.args.get('room_number', type=str)
        
        # معالجة التاريخ
        exam_date_str = request.args.get('exam_date')
        exam_date = datetime.strptime(exam_date_str, '%Y-%m-%d').date() if exam_date_str else None
        
        # معالجة الأوقات
        start_time_str = request.args.get('start_time')
        start_time = datetime.strptime(start_time_str, '%H:%M:%S').time() if start_time_str else None
        
        end_time_str = request.args.get('end_time')
        end_time = datetime.strptime(end_time_str, '%H:%M:%S').time() if end_time_str else None
        
        devices = service.get_alert_devices(
            center_id=center_id,
            room_number=room_number,
            exam_date=exam_date,
            start_time=start_time,
            end_time=end_time
        )
        return jsonify(devices), 200
    except ValueError as e:
        return jsonify({'error': f'Invalid parameter format: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@alert_bp.route('/alerts/mark-and-get', methods=['POST'])
@swag_from({
    'tags': ['Alerts'],
    'description': 'Retrieve alert details and mark unread alerts as read',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'device_id': {'type': 'integer', 'example': 1},
                    'student_id': {'type': 'integer', 'example': 1001},
                    'exam_id': {'type': 'integer', 'example': 5},
                },
                'required': ['device_id', 'student_id', 'exam_id']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Successful operation',
            'schema': {
                'type': 'object',
                'properties': {
                    'device_id': {'type': 'integer'},
                    'student_id': {'type': 'integer'},
                    'exam_id': {'type': 'integer'},
                    'newly_marked_count': {'type': 'integer'},
                    'alerts': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'alert_type': {'type': 'string'},
                                'alert_message': {'type': 'string'},
                                'alert_timestamp': {
                                    'type': 'string',
                                    'format': 'date-time'
                                },
                                'read_status': {
                                    'type': 'string',
                                    'enum': ['Read', 'Unread']
                                }
                            }
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Invalid input',
            'examples': {
                'application/json': {
                    'error': 'Device ID, student ID and exam ID are required'
                }
            }
        },
        500: {
            'description': 'Server error',
            'examples': {
                'application/json': {
                    'error': 'Failed to process the request'
                }
            }
        }
    }
})
def get_and_mark_alerts():
    """
    Retrieve cheating alerts and update unread ones to read status

    Returns all alerts for specified device/student/exam combination
    while marking any unread alerts as read.
    """
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        student_id = data.get('student_id')
        exam_id = data.get('exam_id')

        if None in [device_id, student_id, exam_id]:
            return jsonify({
                'error': 'Device ID, student ID and exam ID are required'
            }), 400

        result = service.get_and_mark_alerts(
            device_id=device_id,
            student_id=student_id,
            exam_id=exam_id
        )

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            'error': f'Failed to process the request: {str(e)}'
        }), 500


# او استخدام get  في التعديل وجلب البيانات 
# @alert_bp.route('/alerts/mark-and-get', methods=['GET'])
# @swag_from({
#     'tags': ['Alerts'],
#     'description': 'Retrieve alert details and mark unread alerts as read',
#     'parameters': [
#         {
#             'name': 'device_id',
#             'in': 'query',
#             'type': 'integer',
#             'required': True,
#             'description': 'ID of the monitoring device',
#             'example': 1
#         },
#         {
#             'name': 'student_id',
#             'in': 'query',
#             'type': 'integer',
#             'required': True,
#             'description': 'ID of the student',
#             'example': 1001
#         },
#         {
#             'name': 'exam_id',
#             'in': 'query',
#             'type': 'integer',
#             'required': True,
#             'description': 'ID of the exam',
#             'example': 5
#         }
#     ],
#     'responses': {
#         200: {
#             'description': 'Successful operation',
#             'schema': {
#                 'type': 'object',
#                 'properties': {
#                     'device_id': {
#                         'type': 'integer',
#                         'example': 1
#                     },
#                     'student_id': {
#                         'type': 'integer',
#                         'example': 1001
#                     },
#                     'exam_id': {
#                         'type': 'integer',
#                         'example': 5
#                     },
#                     'newly_marked_count': {
#                         'type': 'integer',
#                         'description': 'Number of alerts that were marked as read',
#                         'example': 3
#                     },
#                     'alerts': {
#                         'type': 'array',
#                         'items': {
#                             'type': 'object',
#                             'properties': {
#                                 'alert_type': {
#                                     'type': 'string',
#                                     'example': 'Looking around'
#                                 },
#                                 'alert_message': {
#                                     'type': 'string',
#                                     'example': 'Student looking at neighbor\'s screen'
#                                 },
#                                 'alert_timestamp': {
#                                     'type': 'string',
#                                     'format': 'date-time',
#                                     'example': '2023-05-15T10:30:00'
#                                 },
#                                 'read_status': {
#                                     'type': 'string',
#                                     'enum': ['Read', 'Unread'],
#                                     'example': 'Read'
#                                 }
#                             }
#                         }
#                     }
#                 }
#             }
#         },
#         400: {
#             'description': 'Invalid input',
#             'examples': {
#                 'application/json': {
#                     'error': 'Device ID, student ID and exam ID are required'
#                 }
#             }
#         },
#         500: {
#             'description': 'Server error',
#             'examples': {
#                 'application/json': {
#                     'error': 'Failed to process the request'
#                 }
#             }
#         }
#     }
# })
# def get_and_mark_alerts():
#     """
#     Retrieve cheating alerts and update unread ones to read status
    
#     Returns all alerts for specified device/student/exam combination
#     while marking any unread alerts as read.
#     """
#     try:
#         device_id = request.args.get('device_id', type=int)
#         student_id = request.args.get('student_id', type=int)
#         exam_id = request.args.get('exam_id', type=int)
        
#         if None in [device_id, student_id, exam_id]:
#             return jsonify({
#                 'error': 'Device ID, student ID and exam ID are required'
#             }), 400
            
#         result = service.get_and_mark_alerts(
#             device_id=device_id,
#             student_id=student_id,
#             exam_id=exam_id
#         )
        
#         return jsonify(result), 200
        
#     except Exception as e:
#         return jsonify({
#             'error': f'Failed to process the request: {str(e)}'
#         }), 500






#-------------------------------------------------------------------
# @alert_bp.route('/', methods=['GET'])
# @swag_from({
#     'tags': ['Alerts'],
#     'description': 'Get alerts with filters',
#     'parameters': [
#         {
#             'name': 'exam_id',
#             'in': 'query',
#             'type': 'integer',
#             'required': False
#         },
#         {
#             'name': 'student_id',
#             'in': 'query',
#             'type': 'integer',
#             'required': False
#         },
#         {
#             'name': 'is_read',
#             'in': 'query',
#             'type': 'boolean',
#             'required': False
#         },
#         {
#             'name': 'limit',
#             'in': 'query',
#             'type': 'integer',
#             'default': 100
#         }
#     ],
#     'responses': {
#         200: {
#             'description': 'List of alerts',
#             'examples': {
#                 'application/json': [{
#                     'alert_id': 1,
#                     'exam_id': 1,
#                     'student_id': 1001,
#                     'device_id': 5,
#                     'alert_type': 1,
#                     'alert_message': 'Student using phone',
#                     'is_read': False,
#                     'type_name': 'Cheating',
#                     'device_number': 5,
#                     'alert_timestamp': '2023-05-20T14:30:00'
#                 }]
#             }
#         },
#         500: {'description': 'Server error'}
#     }
# })
# def get_alerts():
#     try:
#         exam_id = request.args.get('exam_id', type=int)
#         student_id = request.args.get('student_id', type=int)
#         is_read = request.args.get('is_read', type=lambda x: x.lower() == 'true')
#         limit = request.args.get('limit', 100, type=int)
        
#         alerts = service.get_alerts(
#             exam_id=exam_id,
#             student_id=student_id,
#             is_read=is_read,
#             limit=limit
#         )
#         return jsonify(alerts)
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @alert_bp.route('/<int:alert_id>', methods=['GET'])
# @swag_from({
#     'tags': ['Alerts'],
#     'description': 'Get alert details',
#     'parameters': [{
#         'name': 'alert_id',
#         'in': 'path',
#         'type': 'integer',
#         'required': True
#     }],
#     'responses': {
#         200: {
#             'description': 'Alert details',
#             'examples': {
#                 'application/json': {
#                     'alert_id': 1,
#                     'exam_id': 1,
#                     'student_id': 1001,
#                     'device_id': 5,
#                     'alert_type': 1,
#                     'alert_message': 'Student using phone',
#                     'is_read': False,
#                     'type_name': 'Cheating',
#                     'device_number': 5,
#                     'alert_timestamp': '2023-05-20T14:30:00'
#                 }
#             }
#         },
#         404: {'description': 'Alert not found'},
#         500: {'description': 'Server error'}
#     }
# })
# def get_alert(alert_id):
#     try:
#         alert = service.get_alert(alert_id)
#         return jsonify(alert)
#     except ValueError as e:
#         return jsonify({'error': str(e)}), 404
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @alert_bp.route('/read', methods=['PATCH'])
# @swag_from({
#     'tags': ['Alerts'],
#     'description': 'Mark alerts as read',
#     'parameters': [{
#         'name': 'body',
#         'in': 'body',
#         'required': True,
#         'schema': {
#             'type': 'object',
#             'properties': {
#                 'alert_ids': {
#                     'type': 'array',
#                     'items': {'type': 'integer'},
#                     'example': [1, 2, 3]
#                 }
#             },
#             'required': ['alert_ids']
#         }
#     }],
#     'responses': {
#         200: {
#             'description': 'Number of updated alerts',
#             'examples': {'application/json': {'updated': 3}}
#         },
#         400: {'description': 'Invalid input'},
#         500: {'description': 'Server error'}
#     }
# })
# def mark_alerts_read():
#     data = request.get_json()
#     try:
#         updated = service.mark_alerts_read(data.get('alert_ids', []))
#         return jsonify({'updated': updated})
#     except ValueError as e:
#         return jsonify({'error': str(e)}), 400
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @alert_bp.route('/', methods=['DELETE'])
# @swag_from({
#     'tags': ['Alerts'],
#     'description': 'Delete alerts',
#     'parameters': [{
#         'name': 'body',
#         'in': 'body',
#         'required': True,
#         'schema': {
#             'type': 'object',
#             'properties': {
#                 'alert_ids': {
#                     'type': 'array',
#                     'items': {'type': 'integer'},
#                     'example': [1, 2, 3]
#                 }
#             },
#             'required': ['alert_ids']
#         }
#     }],
#     'responses': {
#         200: {
#             'description': 'Number of deleted alerts',
#             'examples': {'application/json': {'deleted': 3}}
#         },
#         400: {'description': 'Invalid input'},
#         500: {'description': 'Server error'}
#     }
# })
# def delete_alerts():
#     data = request.get_json()
#     try:
#         deleted = service.delete_alerts(data.get('alert_ids', []))
#         return jsonify({'deleted': deleted})
#     except ValueError as e:
#         return jsonify({'error': str(e)}), 400
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
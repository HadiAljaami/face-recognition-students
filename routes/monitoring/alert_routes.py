from flask import Blueprint, request, jsonify
from flasgger import swag_from
from services.monitoring.alert_service import AlertService
from datetime import date, time, datetime
alert_bp = Blueprint('alerts', __name__, url_prefix='/api/alerts')
service = AlertService()

def convert_time_to_str(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, time):
        return obj.strftime("%H:%M:%S")
    return obj


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
                    "alert_id": 13,
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

@alert_bp.route('/<int:student_id>/cheating-reports', methods=['GET'])
@swag_from({
    'tags': ['Cheating Statistics'],
    'summary': 'Get detailed cheating reports for a specific student',
    'parameters': [
        {
            'name': 'student_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the student to retrieve cheating reports for'
        }
    ],
    'responses': {
        200: {
            'description': 'List of cheating reports grouped by exam',
            'examples': {
                'application/json': [
                    {
                        
                    "alerts_details": [
                        {
                            "alert_id": 7,
                            "alert_message": "Student using phone",
                            "alert_timestamp": "2025-04-07T16:30:04.47731",
                            "alert_type": "النظر إلى اليمين",
                            "is_read": "true"
                        },
                        {
                            "alert_id": 6,
                            "alert_message": "Student using phone",
                            "alert_timestamp": "2025-04-07T13:28:38.701102",
                            "alert_type": "النظر إلى اليمين",
                            "is_read":"true"
                        }
                        ],
                        "center_name": "computer",
                        "college_name": "االحاسوب وتكنلوجيا المعلومات",
                        "course_name": "Introduction to Computer Science",
                        "exam_date": "Thu, 15 Dec 2033 00:00:00 GMT",
                        "exam_end_time": "11:00:00",
                        "exam_id": 10,
                        "exam_start_time": "09:00:00",
                        "level_name": "First Year",
                        "major_name": "علوم حاسوب",
                        "room_number": "A101",
                        "semester_name": "الترم الثاني",
                        "student_id": 1001,
                        "total_alerts": 2,
                        "year_name": "2024-2025"
                    }
                ]
            }
        },
        404: {
            'description': 'No cheating reports found for the given student'
        },
        400: {
            'description': 'Invalid student ID'
        }
    }
})

def get_student_cheating_reports(student_id):
    """
    Get detailed cheating reports for a specific student by ID.
    """
    try:
        reports = service.get_student_cheating_reports(student_id)

        for row in reports:
                row['exam_start_time'] = convert_time_to_str(row['exam_start_time'])
                row['exam_end_time'] = convert_time_to_str(row['exam_end_time'])

                # إذا احتجت تحويل تواريخ أو تفاصيل داخل JSON_AGG
                if isinstance(row['alerts_details'], list):
                    for alert in row['alerts_details']:
                        alert['alert_timestamp'] = convert_time_to_str(alert['alert_timestamp'])

        if not reports:
            return jsonify({'message': 'No cheating reports found for this student.'}), 404

        return jsonify(reports), 200

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@alert_bp.route('/alerts-colleges', methods=['GET'])
@swag_from({
    'tags': ['Cheating Statistics'],
    'summary': 'Get cheating statistics by college',
    'description': 'Retrieves cheating statistics grouped by college and academic year with optional year filter',
    'parameters': [
        {
            'name': 'year_id',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'Academic year ID to filter results (optional)'
        }
    ],
    'responses': {
        200: {
            'description': 'List of college cheating statistics',
            'examples': {
                'application/json': [
                    {
                        "college_name": "College of Engineering",
                        "academic_year": "2023",
                        "total_cheating_cases": 45,
                        "cheating_students_count": 30
                    },
                    {
                        "college_name": "College of Medicine",
                        "academic_year": "2023",
                        "total_cheating_cases": 30,
                        "cheating_students_count": 22
                    }
                ]
            }
        },
        404: {
            'description': 'No statistics found for the specified criteria'
        },
        400: {
            'description': 'Invalid year ID provided'
        },
        500: {
            'description': 'Internal server error'
        }
    }
})
def get_college_cheating_stats():
    """
    Get cheating statistics grouped by college and academic year
    
    Args:
        year_id (optional): Academic year ID to filter results
        
    Returns:
        JSON response containing:
        - college_name: Name of the college
        - academic_year: Academic year name
        - total_cheating_cases: Total number of cheating cases
        - cheating_students_count: Number of distinct students who cheated
    """
    try:
        # Get optional year_id parameter
        year_id = request.args.get('year_id', type=int)
        
        # Validate year_id if provided
        if year_id is not None and year_id <= 0:
            return jsonify({
                'error': 'Year ID must be a positive integer',}), 400

        # Get statistics from service
        stats = service.get_college_cheating_stats(year_id)

        if not stats:
            return jsonify({'message': 'No cheating statistics found for the specified criteria',}), 404

        return jsonify(stats), 200

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@alert_bp.route('/alerts-major-level', methods=['GET'])
@swag_from({
    'tags': ['Cheating Statistics'],
    'summary': 'Get cheating stats by major, level, year and college',
    'parameters': [
        {
            'name': 'college_id',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'Filter by college ID'
        },
        {
            'name': 'year_id',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'Filter by academic year ID'
        }
    ],
    'responses': {
        200: {
            'description': 'List of cheating stats',
            'examples': {
                'application/json': [
                    {
                        "college_name": "الحاسوب وتكنولوجيا المعلومات",
                        "major_name": "علوم حاسوب",
                        "level_name": "السنة الأولى",
                        "year_name": "2023-2024",
                        "total_alerts": 15,
                        "alerted_students_count": 10
                    }
                ]
            }
        },
        400: {'description': 'Invalid input'},
        404: {'description': 'No data found'},
        500: {'description': 'Server error'}
    }
})
def get_major_level_stats():
    """
    Get cheating statistics grouped by major, academic level and year
    
    Optional query parameters:
    - college_id: Filter by specific college
    - year_id: Filter by specific academic year
    
    Returns:
    JSON response containing statistics for each major/level/year combination including:
    - major_name: Name of the academic major
    - level_name: Academic level (e.g., First Year)
    - year_name: Academic year name
    - total_alerts: Total number of cheating alerts
    - alerted_students_count: Number of distinct students who cheated
    """
    try:
        # Get optional query parameters
        college_id = request.args.get('college_id', type=int)
        year_id = request.args.get('year_id', type=int)

        if college_id is not None and college_id <= 0:
            return jsonify({'error': 'College ID must be positive'}), 400
        if year_id is not None and year_id <= 0:
            return jsonify({'error': 'Year ID must be positive'}), 400        
                
        stats = service.get_major_level_stats(college_id, year_id)
        
        return jsonify(stats), 200
        
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@alert_bp.route('/course-stats', methods=['GET'])
@swag_from({
    'tags': ['Cheating Statistics'],
    'summary': 'Get cheating stats by course',
    'parameters': [
        {
            'name': 'college_id',
            'in': 'query',
            'type': 'integer',
            'required': True,
            'description': 'College ID (required)'
        },
        {
            'name': 'major_id',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'Major ID filter'
        },
        {
            'name': 'level_id',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'Level ID filter'
        },
        {
            'name': 'year_id',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'Academic year ID filter'
        }
    ],
    'responses': {
        200: {
            'description': 'Success',
            'examples': {
                'application/json': {
                    'success': True,
                    'data': [
                        {
                            'course_name': 'Math 101',
                            'total_cheating_cases': 5,
                            'cheating_students_count': 3,
                            'exam_date': '2023-05-15',
                            'semester_name': 'Fall',
                            'academic_year': '2023-2024',
                            'major_name': 'Computer Science',
                            'level_name': 'First Year'
                        }
                    ]
                }
            }
        },
        400: {
            'description': 'Invalid input',
            'examples': {
                'application/json': {
                    'success': False,
                    'error': 'Invalid college ID'
                }
            }
        },
        404: {
            'description': 'No data found',
            'examples': {
                'application/json': {
                    'success': False,
                    'error': 'No data found'
                }
            }
        },
        500: {
            'description': 'Server error',
            'examples': {
                'application/json': {
                    'success': False,
                    'error': 'Database error'
                }
            }
        }
    }
})
def get_course_stats():
    """
    Get cheating statistics grouped by course
    
    Returns JSON with:
    - success: boolean status
    - data: list of stats if success
    - error: message if failed
    """
    college_id = request.args.get('college_id', type=int)
    major_id = request.args.get('major_id', type=int,default=None)
    level_id = request.args.get('level_id', type=int,default=None)
    year_id = request.args.get('year_id', type=int,default=None)

    # Validate mandatory college_id
    if college_id is None:
        return jsonify({'error': 'College ID is required'}), 400
    if college_id <= 0:
        return jsonify({'error': 'College ID must be a positive number'}), 400

    # Validate optional parameters (must be positive if provided)
    if major_id is not None and major_id <= 0:
        return jsonify({'error': 'Major ID must be a positive number'}), 400
    if level_id is not None and level_id <= 0:
        return jsonify({'error': 'Level ID must be a positive number'}), 400
    if year_id is not None and year_id <= 0:
        return jsonify({'error': 'Year ID must be a positive number'}), 400

    try:
        result = service.get_course_stats(college_id, major_id, level_id, year_id)
        
        if not result:
            return jsonify({'error': 'No data found'}), 404
         
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({ 'error': 'Server error'}), 500

@alert_bp.route('/', methods=['DELETE'])
@swag_from({
    'tags': ['Alerts'],
    'description': 'Delete alerts',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'alert_ids': {
                    'type': 'array',
                    'items': {'type': 'integer'},
                    'example': [1, 2, 3]
                }
            },
            'required': ['alert_ids']
        }
    }],
    'responses': {
        200: {
            'description': 'Number of deleted alerts',
            'examples': {'application/json': {'deleted': 3}}
        },
        400: {'description': 'Invalid input'},
        500: {'description': 'Server error'}
    }
})
def delete_alerts():
    data = request.get_json()
    try:
        deleted = service.delete_alerts(data.get('alert_ids', []))
        return jsonify({'deleted': deleted})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@alert_bp.route('/delete-multiple', methods=['POST'])
@swag_from({
    'tags': ['Alerts'],
    'description': 'Delete multiple alerts by student, exam, and device.',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'items': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'exam_id': {'type': 'integer', 'example': 101},
                            'student_id': {'type': 'string', 'example': 'S1'},
                            'device_id': {'type': 'integer', 'example': 10}
                        },
                        'required': ['exam_id', 'student_id', 'device_id']
                    }
                }
            },
            'required': ['items']
        }
    }],
    'responses': {
        200: {
            'description': 'Alerts deleted successfully',
            'examples': {
                'application/json': {
                    'message': '3 alerts deleted'
                }
            }
        },
        400: {
            'description': 'Invalid input',
            'examples': {
                'application/json': {
                    'error': 'No alert keys provided for deletion'
                }
            }
        },
        500: {
            'description': 'Internal server error',
            'examples': {
                'application/json': {
                    'error': 'Service error while deleting alerts: ...'
                }
            }
        }
    }
})
def delete_multiple_alerts():
    data = request.get_json()

    if not data or "items" not in data:
        return jsonify({"error": "Missing 'items' list"}), 400

    try:
        deleted_count = service.delete_multiple_alerts(data["items"])
        return jsonify({
            "message": f"{deleted_count} alert(s) deleted successfully"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



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
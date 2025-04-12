from flask import Blueprint, request, jsonify
from flasgger import swag_from
from services.academic.exam_distribution_service import ExamDistributionService

exam_distribution_bp = Blueprint('exam_distributions', __name__, url_prefix='/api/exam-distributions')
service = ExamDistributionService()

SWAGGER_TEMPLATE = {
    'definitions': {
        'ExamDistribution': {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer', 'example': 1},
                'student_id': {'type': 'string', 'example': '2023001'},
                'student_name': {'type': 'string', 'example': 'أحمد محمد'},
                'exam_id': {'type': 'integer', 'example': 1},
                'device_id': {'type': 'integer', 'example': 5},
                'exam_date': {'type': 'string', 'format': 'date', 'example': '2023-12-15'},
                'course_name': {'type': 'string', 'example': 'قواعد البيانات'},
                'major_name': {'type': 'string', 'example': 'علوم الحاسب'},
                'college_name': {'type': 'string', 'example': 'كلية الحوسبة'},
                'assigned_at': {'type': 'string', 'format': 'date-time'}
            },
            'required': ['student_id', 'student_name', 'exam_id']
        }
    }
}

def merge_swagger(config):
    return {**config, **SWAGGER_TEMPLATE}



@exam_distribution_bp.route('/', methods=['POST'])
@swag_from({
    'tags': ['Exam Distributions'],
    'description': 'Assign exam to student',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'student_id': {'type': 'string', 'example': '2023001'},
                'student_name': {'type': 'string', 'example': 'أحمد محمد'},
                'exam_id': {'type': 'integer', 'example': 1},
                'device_id': {'type': 'integer', 'example': 5}
            },
            'required': ['student_id', 'student_name', 'exam_id']
        }
    }],
    'responses': {
        201: {
            'description': 'Exam assigned',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Student exam assignment inserted successfully'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer', 'example': 1},
                            'student_id': {'type': 'string', 'example': '2023001'},
                            'student_name': {'type': 'string', 'example': 'أحمد محمد'},
                            'exam_id': {'type': 'integer', 'example': 1},
                            'device_id': {'type': 'integer', 'example': 5},
                            'exam_date': {'type': 'string', 'format': 'date', 'example': '2023-12-15'},
                            'course_name': {'type': 'string', 'example': 'قواعد البيانات'},
                            'major_name': {'type': 'string', 'example': 'علوم الحاسب'},
                            'college_name': {'type': 'string', 'example': 'كلية الحوسبة'},
                            'assigned_at': {'type': 'string', 'format': 'date-time'}
                        }
                    }
                }
            }
        },
        400: {'description': 'Validation error'},
        404: {'description': 'Reference not found'},
        409: {'description': 'Exam already assigned'},
        500: {'description': 'Server error'}
    }
})
def assign_exam():
    data = request.get_json()
    try:
        # تحقق من الحقول المطلوبة
        if not all(k in data for k in ['student_id', 'student_name', 'exam_id']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        result = service.assign_exam_to_student(
            student_id=data['student_id'],
            student_name=data['student_name'],
            exam_id=data['exam_id'],
            device_id=data.get('device_id')
        )
       
        if not result:
            return jsonify({'error': 'Failed to create distribution'}), 500

        action_msg = 'inserted' if result.get('action') == 'insert' else 'updated'
        result.pop('action', None)  # نحذف "action" لأنها داخلية

        return jsonify({
            'message': f'Student exam assignment {action_msg} successfully',
            'data': result
        }), 201

    except ValueError as e:
        error_msg = str(e)
       
        if "already assigned" in error_msg:
            return jsonify({'error': error_msg}), 409
        elif "Device not found" in error_msg:
            return jsonify({'error': "Device not found."}), 404
        elif "Exam not found" in error_msg:
            return jsonify({'error': "Exam not found."}), 404
        else:
            return jsonify({'error': error_msg}), 400

    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500




# @exam_distribution_bp.route('/', methods=['POST'])
# @swag_from({
#     'tags': ['Exam Distributions'],
#     'description': 'Assign exam to student',
#     'parameters': [{
#         'name': 'body',
#         'in': 'body',
#         'required': True,
#         'schema': {
#             'type': 'object',
#             'properties': {
#                 'student_id': {'type': 'string', 'example': '2023001'},
#                 'student_name': {'type': 'string', 'example': 'أحمد محمد'},
#                 'exam_id': {'type': 'integer', 'example': 1},
#                 'device_id': {'type': 'integer', 'example': 5}
#             },
#             'required': ['student_id', 'student_name', 'exam_id']
#         }
#     }],
#     'responses': {
#         201: {
#             'description': 'Exam assigned',
#             'schema': {
#                 'type': 'object',
#                 'properties': {
#                     'id': {'type': 'integer', 'example': 1},
#                     'student_id': {'type': 'string', 'example': '2023001'},
#                     'student_name': {'type': 'string', 'example': 'أحمد محمد'},
#                     'exam_id': {'type': 'integer', 'example': 1},
#                     'device_id': {'type': 'integer', 'example': 5},
#                     'exam_date': {'type': 'string', 'format': 'date', 'example': '2023-12-15'},
#                     'course_name': {'type': 'string', 'example': 'قواعد البيانات'},
#                     'major_name': {'type': 'string', 'example': 'علوم الحاسب'},
#                     'college_name': {'type': 'string', 'example': 'كلية الحوسبة'},
#                     'assigned_at': {'type': 'string', 'format': 'date-time'}
#                 }
#             }
#         },
#         400: {'description': 'Validation error'},
#         404: {'description': 'Reference not found'},
#         409: {'description': 'Exam already assigned'},
#         500: {'description': 'Server error'}
#     }
# })
# def assign_exam():
#     data = request.get_json()
#     try:
#         # التحقق من البيانات المطلوبة
#         if not all(k in data for k in ['student_id', 'student_name', 'exam_id']):
#             return jsonify({'error': 'Missing required fields'}), 400
            
#         result = service.assign_exam_to_student(
#             student_id=data['student_id'],
#             student_name=data['student_name'],
#             exam_id=data['exam_id'],
#             device_id=data.get('device_id')
#         )
        
#         if not result:
#             return jsonify({'error': 'Failed to create distribution'}), 500
#         print (result)    
#         return jsonify(result), 201
        
#     except ValueError as e:
#         error_msg = str(e)
#         if "already assigned" in error_msg:
#             return jsonify({'error': error_msg}), 409
#         elif "Invalid reference" in error_msg:
#             return jsonify({'error': error_msg}), 404
#         else:
#             return jsonify({'error': error_msg}), 400
            
#     except Exception as e:
#         return jsonify({'error': 'Internal server error'}), 500
    
@exam_distribution_bp.route('/batch-delete', methods=['DELETE'])
@swag_from({
    'tags': ['Exam Distributions'],
    'description': 'Delete multiple distributions',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'distribution_ids': {
                    'type': 'array',
                    'items': {'type': 'integer'},
                    'example': [1, 2, 3]
                }
            },
            'required': ['distribution_ids']
        }
    }],
    'responses': {
        200: {
            'description': 'Delete count',
            'schema': {
                'type': 'object',
                'properties': {
                    'deleted_count': {'type': 'integer'}
                }
            }
        },
        400: {'description': 'Invalid IDs'},
        500: {'description': 'Server error'}
    }
})
def delete_multiple_distributions():
    data = request.get_json()

    # التحقق من وجود الحقل المطلوب
    if not data or 'distribution_ids' not in data:
        return jsonify({'error': 'Missing distribution_ids in request body'}), 400
    try:
        deleted_count = service.delete_multiple_distributions(data['distribution_ids'])
        return jsonify({'deleted_count': deleted_count}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception:
        return jsonify({'error': 'Server error'}), 500
    
@exam_distribution_bp.route('/<int:distribution_id>', methods=['PUT'])
@swag_from({
    'tags': ['Exam Distributions'],
    'description': 'Update an existing exam distribution',
    'parameters': [
        {
            'name': 'distribution_id',
            'in': 'path',
            'description': 'ID of the distribution record',
            'type': 'integer',
            'required': True,
            'example': 1
        },
        {
            'name': 'body',
            'in': 'body',
            'description': 'Distribution data to update',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'student_name': {'type': 'string', 'example': 'أحمد محمد', 'description': 'Updated student name'},
                    'exam_id': {'type': 'integer', 'example': 5, 'description': 'New exam ID'},
                    'device_id': {'type': 'integer', 'example': 3, 'description': 'New device ID'}
                },
                'minProperties': 1  # يجب تحديث حقل واحد على الأقل
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Successfully updated distribution',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'message': {'type': 'string', 'example': 'Distribution updated successfully'},
                    'updated_fields': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'example': ['student_name', 'device_id']
                    }
                }
            }
        },
        400: {
            'description': 'Validation error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'No fields provided for update'}
                }
            }
        },
        404: {
            'description': 'Distribution not found',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Distribution not found'}
                }
            }
        },
        500: {
            'description': 'Internal server error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Internal server error'}
                }
            }
        }
    }
})
def update_distribution(distribution_id):
    data = request.get_json()
    try:
        # التحقق من وجود بيانات للتحديث
        if not data or len(data) == 0:
            return jsonify({'error': 'No fields provided for update'}), 400
            
        result = service.update_exam_distribution(
            distribution_id=distribution_id,
            student_name=data.get('student_name'),
            exam_id=data.get('exam_id'),
            device_id=data.get('device_id')
        )
        
        if not result:
            return jsonify({'error': 'Distribution not found'}), 404
            
        # تحديد الحقول التي تم تحديثها
        updated_fields = [k for k in data if k in ['student_name', 'exam_id', 'device_id']]
        
        return jsonify({
            'id': distribution_id,
            'message': 'Distribution updated successfully',
            'updated_fields': updated_fields
        }), 200
        
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            return jsonify({'error': error_msg}), 404
        return jsonify({'error': error_msg}), 400
    except Exception as e:
        
        return jsonify({'error': 'Internal server error'}), 500
    

@exam_distribution_bp.route('/report/<int:exam_id>', methods=['GET'])
@swag_from({
    'tags': ['Exam Distributions'],
    'description': 'Get exam distribution report by exam ID',
    'parameters': [{
        'name': 'exam_id',
        'in': 'path',
        'type': 'integer',
        'required': True,
        'example': 123
    }],
    'responses': {
        200: {
            'description': 'List of room groups with exam distribution',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'header': {
                            'type': 'object',
                            'properties': {
                                'room_name': {'type': 'string'},
                                'room_number': {'type': 'string'},
                                'center_name': {'type': 'string'},
                                'course_name': {'type': 'string'},
                                'exam_date': {'type': 'string'},
                                'exam_start_time': {'type': 'string'},
                                'exam_end_time': {'type': 'string'},
                                'college_name': {'type': 'string'},
                                'major_name': {'type': 'string'},
                                'level_name': {'type': 'string'},
                                'semester_name': {'type': 'string'},
                                'academic_year': {'type': 'string'}
                            }
                        },
                        'students': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'device_number': {'type': 'integer'},
                                    'student_id': {'type': 'string'},
                                    'student_name': {'type': 'string'}
                                }
                            }
                        }
                    }
                }
            }
        },
        400: {'description': 'Invalid exam ID'},
        404: {'description': 'Exam distribution not found'},
        500: {'description': 'Server error'}
    }
})
def get_exam_report(exam_id):
    try:
        report = service.get_exam_distribution_report(exam_id)
        return jsonify(report), 200
        
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            return jsonify({'error': error_msg}), 404
        return jsonify({'error': error_msg}), 400
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@exam_distribution_bp.route('/student-info/<string:student_id>', methods=['GET'])
@swag_from({
    'tags': ['Exam Distributions'],
    'description': 'Get complete student information including exam assignments',
    'parameters': [{
        'name': 'student_id',
        'in': 'path',
        'type': 'string',
        'required': True,
        'example': '2023001',
        'description': 'University registration number'
    }],
    'responses': {
        200: {
            'description': 'Student information retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': True},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'student_id': {'type': 'string', 'example': '2023001'},
                            'student_name': {'type': 'string', 'example': 'John Doe'},
                            'device_number': {'type': 'integer', 'example': 5},
                            'room_number': {'type': 'string', 'example': 'A101'},
                            'center_name': {'type': 'string', 'example': 'Main Exam Center'},
                            'exam_info': {
                                'type': 'object',
                                'properties': {
                                    'exam_id': {'type': 'integer', 'example': 1},
                                    'exam_date': {'type': 'string', 'example': '2023-05-15'},
                                    'exam_start_time': {'type': 'string', 'example': '09:00:00'},
                                    'exam_end_time': {'type': 'string', 'example': '11:00:00'},
                                    'course_name': {'type': 'string', 'example': 'Mathematics'}
                                }
                            },
                            'academic_info': {
                                'type': 'object',
                                'properties': {
                                    'college_name': {'type': 'string', 'example': 'College of Science'},
                                    'major_name': {'type': 'string', 'example': 'Computer Science'},
                                    'level_name': {'type': 'string', 'example': 'Third Year'},
                                    'semester_name': {'type': 'string', 'example': 'Second Semester'},
                                    'academic_year': {'type': 'string', 'example': '2022-2023'}
                                }
                            }
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Invalid student ID format',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Valid student ID must be provided'}
                }
            }
        },
        404: {
            'description': 'Student not found',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Student not found in the system'}
                }
            }
        },
        500: {
            'description': 'Internal server error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Database operation failed'}
                }
            }
        }
    }
})
def get_student_information(student_id):
    """
    Retrieve complete student information including exam assignments and academic details
    
    This endpoint returns:
    - Basic student information
    - Device and room assignment details
    - Exam schedule information
    - Academic program details
    """
    try:
        result = service.get_student_info(student_id)
        return jsonify(result), 200
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            return jsonify({'error': error_msg}), 404
        return jsonify({'error': error_msg}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

from flask import Blueprint, request, jsonify
from flasgger import swag_from
from services.monitoring.model_config_service import ModelConfigService

model_config_bp = Blueprint('model_config', __name__, url_prefix='/api/model-config')

# Initialize repository and service

service = ModelConfigService()

@model_config_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['Model Config'],
    'description': 'Get current model configuration',
    'responses': {
        200: {
            'description': 'Current configuration',
            'examples': {
                'application/json': {
                    "id": 1,
                    "faceMeshOptions": {
                        "maxNumFaces": 1,
                        "refineLandmarks": True,
                        "minDetectionConfidence": 0.7,
                        "minTrackingConfidence": 0.7
                    },
                    "poseOptions": {
                        "modelComplexity": 1,
                        "smoothLandmarks": True,
                        "enableSegmentation": False,
                        "smoothSegmentation": False,
                        "minDetectionConfidence": 0.7,
                        "minTrackingConfidence": 0.7
                    },
                    "camera": {
                        "width": 800,
                        "height": 600
                    },
                    "attentionDecrementFactor": 5,
                    "attentionIncrementFactor": 1,
                    "noFaceDecrementFactor": 3,
                    "alerts": {
                        "head": {
                            "downThreshold": 0.8,
                            "lateralThreshold": 0.7,
                            "duration": 3000,
                            "enabled": {
                                "down": True,
                                "left": False,
                                "right": False
                            },
                            "detectTurnOnly": True
                        },
                        "mouth": {
                            "threshold": 0.01,
                            "duration": 10000,
                            "enabled": True
                        }
                    },
                    "updated_at": "2023-05-20T12:34:56.789Z"
                }
            }
        },
        500: {'description': 'Server error'}
    }
})
def get_config():
    try:
        config = service.get_current_config()
        return jsonify(config), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# @model_config_bp.route('/<int:config_id>', methods=['PUT'])
# @swag_from({
#     'tags': ['Model Config'],
#     'description': 'Update model configuration',
#     'parameters': [{
#         'name': 'config_id',
#         'in': 'path',
#         'type': 'integer',
#         'required': True
#     }, {
#         'name': 'body',
#         'in': 'body',
#         'required': True,
#         'schema': {
#             'type': 'object',
#             'properties': {
#                 'faceMeshOptions': {
#                     'type': 'object',
#                     'properties': {
#                         'maxNumFaces': {'type': 'integer'},
#                         'refineLandmarks': {'type': 'boolean'},
#                         'minDetectionConfidence': {'type': 'number'},
#                         'minTrackingConfidence': {'type': 'number'}
#                     }
#                 },
#                 'poseOptions': {
#                     'type': 'object',
#                     'properties': {
#                         'modelComplexity': {'type': 'integer'},
#                         'smoothLandmarks': {'type': 'boolean'},
#                         'enableSegmentation': {'type': 'boolean'},
#                         'smoothSegmentation': {'type': 'boolean'},
#                         'minDetectionConfidence': {'type': 'number'},
#                         'minTrackingConfidence': {'type': 'number'}
#                     }
#                 },
#                 'camera': {
#                     'type': 'object',
#                     'properties': {
#                         'width': {'type': 'integer'},
#                         'height': {'type': 'integer'}
#                     }
#                 },
#                 'attentionDecrementFactor': {'type': 'integer'},
#                 'attentionIncrementFactor': {'type': 'integer'},
#                 'noFaceDecrementFactor': {'type': 'integer'},
#                 'alerts': {
#                     'type': 'object',
#                     'properties': {
#                         'head': {
#                             'type': 'object',
#                             'properties': {
#                                 'downThreshold': {'type': 'number'},
#                                 'lateralThreshold': {'type': 'number'},
#                                 'duration': {'type': 'integer'},
#                                 'enabled': {
#                                     'type': 'object',
#                                     'properties': {
#                                         'down': {'type': 'boolean'},
#                                         'left': {'type': 'boolean'},
#                                         'right': {'type': 'boolean'}
#                                     }
#                                 },
#                                 'detectTurnOnly': {'type': 'boolean'}
#                             }
#                         },
#                         'mouth': {
#                             'type': 'object',
#                             'properties': {
#                                 'threshold': {'type': 'number'},
#                                 'duration': {'type': 'integer'},
#                                 'enabled': {'type': 'boolean'}
#                             }
#                         }
#                     }
#                 }
#             }
#         }
#     }],
#     'responses': {
#         200: {'description': 'Configuration updated successfully'},
#         400: {'description': 'Invalid input'},
#         500: {'description': 'Server error'}
#     }
# })

# def update_config(config_id):
#     try:
#         data = request.get_json()
#         service.update_config(config_id, data)
#         return jsonify({"message": "Configuration updated successfully"}), 200
#     except ValueError as e:
#         return jsonify({"error": str(e)}), 400
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


@model_config_bp.route('/<int:config_id>', methods=['PUT'])
@swag_from({
    'tags': ['Model Config'],
    'description': 'Update model configuration with new parameters',
    'parameters': [{
        'name': 'config_id',
        'in': 'path',
        'type': 'integer',
        'required': True,
        'description': 'ID of the configuration to update'
    }, {
        'name': 'body',
        'in': 'body',
        'required': True,
        'description': 'Configuration object with updated values',
        'schema': {
            'type': 'object',
            'properties': {
                'faceMeshOptions': {
                    'type': 'object',
                    'properties': {
                        'maxNumFaces': {
                            'type': 'integer',
                            'default': 1,
                            'minimum': 1,
                            'maximum': 10,
                            'description': 'Maximum number of faces to detect'
                        },
                        'refineLandmarks': {
                            'type': 'boolean',
                            'default': True,
                            'description': 'Whether to refine face landmarks'
                        },
                        'minDetectionConfidence': {
                            'type': 'number',
                            'default': 0.7,
                            'minimum': 0,
                            'maximum': 1,
                            'description': 'Minimum confidence for face detection'
                        },
                        'minTrackingConfidence': {
                            'type': 'number',
                            'default': 0.7,
                            'minimum': 0,
                            'maximum': 1,
                            'description': 'Minimum confidence for face tracking'
                        }
                    },
                    'description': 'Face mesh detection settings'
                },
                'poseOptions': {
                    'type': 'object',
                    'properties': {
                        'modelComplexity': {
                            'type': 'integer',
                            'default': 1,
                            'minimum': 0,
                            'maximum': 2,
                            'description': 'Pose model complexity (0=light, 1=full, 2=heavy)'
                        },
                        'smoothLandmarks': {
                            'type': 'boolean',
                            'default': True,
                            'description': 'Whether to smooth pose landmarks'
                        },
                        'enableSegmentation': {
                            'type': 'boolean',
                            'default': False,
                            'description': 'Whether to enable segmentation'
                        },
                        'smoothSegmentation': {
                            'type': 'boolean',
                            'default': False,
                            'description': 'Whether to smooth segmentation'
                        },
                        'minDetectionConfidence': {
                            'type': 'number',
                            'default': 0.7,
                            'minimum': 0,
                            'maximum': 1,
                            'description': 'Minimum confidence for pose detection'
                        },
                        'minTrackingConfidence': {
                            'type': 'number',
                            'default': 0.7,
                            'minimum': 0,
                            'maximum': 1,
                            'description': 'Minimum confidence for pose tracking'
                        }
                    },
                    'description': 'Pose estimation settings'
                },
                'camera': {
                    'type': 'object',
                    'properties': {
                        'width': {
                            'type': 'integer',
                            'default': 800,
                            'minimum': 100,
                            'maximum': 4096,
                            'description': 'Camera resolution width'
                        },
                        'height': {
                            'type': 'integer',
                            'default': 600,
                            'minimum': 100,
                            'maximum': 2160,
                            'description': 'Camera resolution height'
                        }
                    },
                    'description': 'Camera settings'
                },
                'attentionDecrementFactor': {
                    'type': 'integer',
                    'default': 5,
                    'minimum': 1,
                    'description': 'Attention decrease factor when distracted'
                },
                'attentionIncrementFactor': {
                    'type': 'integer',
                    'default': 1,
                    'minimum': 1,
                    'description': 'Attention increase factor when focused'
                },
                'noFaceDecrementFactor': {
                    'type': 'integer',
                    'default': 3,
                    'minimum': 1,
                    'description': 'Attention decrease factor when no face detected'
                },
                'alerts': {
                    'type': 'object',
                    'properties': {
                        'head': {
                            'type': 'object',
                            'properties': {
                                'downThreshold': {
                                    'type': 'number',
                                    'default': 0.8,
                                    'minimum': 0,
                                    'maximum': 1,
                                    'description': 'Threshold for head down detection'
                                },
                                'lateralThreshold': {
                                    'type': 'number',
                                    'default': 0.7,
                                    'minimum': 0,
                                    'maximum': 1,
                                    'description': 'Threshold for head turning detection'
                                },
                                'duration': {
                                    'type': 'integer',
                                    'default': 3000,
                                    'minimum': 100,
                                    'description': 'Duration in ms before triggering alert'
                                },
                                'enabled': {
                                    'type': 'object',
                                    'properties': {
                                        'down': {
                                            'type': 'boolean',
                                            'default': True,
                                            'description': 'Enable head down alerts'
                                        },
                                        'left': {
                                            'type': 'boolean',
                                            'default': False,
                                            'description': 'Enable head left alerts'
                                        },
                                        'right': {
                                            'type': 'boolean',
                                            'default': False,
                                            'description': 'Enable head right alerts'
                                        }
                                    },
                                    'description': 'Enabled head alert directions'
                                },
                                'detectTurnOnly': {
                                    'type': 'boolean',
                                    'default': True,
                                    'description': 'Detect only turning movements'
                                }
                            },
                            'description': 'Head movement alert settings'
                        },
                        'mouth': {
                            'type': 'object',
                            'properties': {
                                'threshold': {
                                    'type': 'number',
                                    'default': 0.01,
                                    'minimum': 0,
                                    'maximum': 1,
                                    'description': 'Threshold for mouth opening detection'
                                },
                                'duration': {
                                    'type': 'integer',
                                    'default': 10000,
                                    'minimum': 100,
                                    'description': 'Duration in ms before triggering alert'
                                },
                                'enabled': {
                                    'type': 'boolean',
                                    'default': True,
                                    'description': 'Enable mouth opening alerts'
                                }
                            },
                            'description': 'Mouth movement alert settings'
                        }
                    },
                    'description': 'Alert system settings'
                }
            },
            'example': {
                "faceMeshOptions": {
                    "maxNumFaces": 1,
                    "refineLandmarks": True,
                    "minDetectionConfidence": 0.7,
                    "minTrackingConfidence": 0.7
                },
                "poseOptions": {
                    "modelComplexity": 1,
                    "smoothLandmarks": True,
                    "enableSegmentation": False,
                    "smoothSegmentation": False,
                    "minDetectionConfidence": 0.7,
                    "minTrackingConfidence": 0.7
                },
                "camera": {
                    "width": 800,
                    "height": 600
                },
                "attentionDecrementFactor": 5,
                "attentionIncrementFactor": 1,
                "noFaceDecrementFactor": 3,
                "alerts": {
                    "head": {
                        "downThreshold": 0.8,
                        "lateralThreshold": 0.7,
                        "duration": 3000,
                        "enabled": {
                            "down": True,
                            "left": False,
                            "right": False
                        },
                        "detectTurnOnly": True
                    },
                    "mouth": {
                        "threshold": 0.01,
                        "duration": 10000,
                        "enabled": True
                    }
                }
            }
        }
    }],
    'responses': {
        200: {
            'description': 'Configuration updated successfully',
            'examples': {
                'application/json': {
                    'message': 'Configuration updated successfully',
                    'config_id': 1
                }
            }
        },
        400: {
            'description': 'Invalid input',
            'examples': {
                'application/json': {
                    'error': 'minDetectionConfidence must be between 0 and 1'
                }
            }
        },
        500: {
            'description': 'Server error',
            'examples': {
                'application/json': {
                    'error': 'Internal server error while updating configuration'
                }
            }
        }
    }
})
def update_config(config_id):
    """
    Update the model configuration with new parameters.
    
    This endpoint allows updating any part of the model configuration including:
    - Face detection settings
    - Pose estimation settings
    - Camera resolution
    - Attention factors
    - Alert system thresholds
    
    All parameters are optional - only provided values will be updated.
    """
    try:
        data = request.get_json()
        service.update_config(config_id, data)
        return jsonify({"message": "Configuration updated successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@model_config_bp.route('/reset-default', methods=['POST'])
@swag_from({
    'tags': ['Model Config'],
    'description': 'Reset configuration to default values',
    'responses': {
        200: {'description': 'Configuration reset to default'},
        500: {'description': 'Server error'}
    }
})
def reset_to_default():
    try:
        service.reset_to_default()
        return jsonify({"message": "Configuration reset to default"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@model_config_bp.route('/default', methods=['GET'])
@swag_from({
    'tags': ['Model Config'],
    'description': 'Get default configuration values',
    'responses': {
        200: {
            'description': 'Default configuration',
            'examples': {
                'application/json': {
                    "faceMeshOptions": {
                        "maxNumFaces": 1,
                        "refineLandmarks": True,
                        "minDetectionConfidence": 0.7,
                        "minTrackingConfidence": 0.7
                    },
                    "poseOptions": {
                        "modelComplexity": 1,
                        "smoothLandmarks": True,
                        "enableSegmentation": False,
                        "smoothSegmentation": False,
                        "minDetectionConfidence": 0.7,
                        "minTrackingConfidence": 0.7
                    },
                    "camera": {
                        "width": 800,
                        "height": 600
                    },
                    "attentionDecrementFactor": 5,
                    "attentionIncrementFactor": 1,
                    "noFaceDecrementFactor": 3,
                    "alerts": {
                        "head": {
                            "downThreshold": 0.8,
                            "lateralThreshold": 0.7,
                            "duration": 3000,
                            "enabled": {
                                "down": True,
                                "left": False,
                                "right": False
                            },
                            "detectTurnOnly": True
                        },
                        "mouth": {
                            "threshold": 0.01,
                            "duration": 10000,
                            "enabled": True
                        }
                    }
                }
            }
        },
        500: {'description': 'Server error'}
    }
})
def get_default_config():
    try:
        default_config = service.get_default_config()
        # Remove id and updated_at from default config response
        default_config.pop("id", None)
        default_config.pop("updated_at", None)
        return jsonify(default_config), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
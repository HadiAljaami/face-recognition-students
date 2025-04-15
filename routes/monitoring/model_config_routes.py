from flask import Blueprint, request, jsonify
from flasgger import swag_from
from services.monitoring.model_config_service import ModelConfigService

model_config_bp = Blueprint('model_config', __name__, url_prefix='/api/model-config')

# إنشاء نسخة من الخدمة
service = ModelConfigService()

@model_config_bp.route('/', methods=['GET'])
@swag_from({
    'tags': ['Model Config'],
    'description': 'استرجاع الإعدادات الحالية للنموذج',
    'responses': {
        200: {
            'description': 'الإعدادات الحالية',
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
                            "upThreshold": -0.5,
                            "downThreshold": 0.5,
                            "lateralThreshold": 15,
                            "duration": 3000,
                            "enabled": {
                                "up": True,
                                "down": True,
                                "left": True,
                                "right": True,
                                "forward": True
                            },
                            "detectTurnOnly": True
                        },
                        "mouth": {
                            "threshold": 0.05,
                            "duration": 3000,
                            "enabled": True
                        },
                        "gaze": {
                            "duration": 3000,
                            "enabled": True
                        },
                        "headPose": {
                            "neutralRange": 5,
                            "smoothingFrames": 10,
                            "referenceFrames": 30
                        }
                    },
                    "sendDataInterval": 5000,
                    "maxAlerts": 10,
                    "updated_at": "2023-05-20T12:34:56.789Z"
                }
            }
        },
        500: {'description': 'خطأ في الخادم'}
    }
})
def get_config():
    try:
        config = service.get_current_config()
        return jsonify(config), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@model_config_bp.route('/<int:config_id>', methods=['PUT'])
@swag_from({
    'tags': ['Model Config'],
    'description': 'تحديث إعدادات النموذج مع المعطيات الجديدة',
    'parameters': [{
        'name': 'config_id',
        'in': 'path',
        'type': 'integer',
        'required': True,
        'description': 'معرف الإعداد الذي سيتم تحديثه'
    }, {
        'name': 'body',
        'in': 'body',
        'required': True,
        'description': 'كائن يحتوي على الإعدادات المحدّثة',
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
                            'description': 'أقصى عدد من الوجوه للكشف'
                        },
                        'refineLandmarks': {
                            'type': 'boolean',
                            'default': True,
                            'description': 'ما إذا كان يجب تحسين معالم الوجه'
                        },
                        'minDetectionConfidence': {
                            'type': 'number',
                            'default': 0.7,
                            'minimum': 0,
                            'maximum': 1,
                            'description': 'أدنى ثقة للكشف عن الوجه'
                        },
                        'minTrackingConfidence': {
                            'type': 'number',
                            'default': 0.7,
                            'minimum': 0,
                            'maximum': 1,
                            'description': 'أدنى ثقة لتتبع الوجه'
                        }
                    },
                    'description': 'إعدادات كشف شبكة الوجه'
                },
                'poseOptions': {
                    'type': 'object',
                    'properties': {
                        'modelComplexity': {
                            'type': 'integer',
                            'default': 1,
                            'minimum': 0,
                            'maximum': 2,
                            'description': 'تعقيد نموذج الوضع (0=خفيف، 1=كامل، 2=ثقيل)'
                        },
                        'smoothLandmarks': {
                            'type': 'boolean',
                            'default': True,
                            'description': 'ما إذا كان يجب تنعيم معالم الوضع'
                        },
                        'enableSegmentation': {
                            'type': 'boolean',
                            'default': False,
                            'description': 'ما إذا كان يجب تفعيل التجزئة'
                        },
                        'smoothSegmentation': {
                            'type': 'boolean',
                            'default': False,
                            'description': 'ما إذا كان يجب تنعيم التجزئة'
                        },
                        'minDetectionConfidence': {
                            'type': 'number',
                            'default': 0.7,
                            'minimum': 0,
                            'maximum': 1,
                            'description': 'أدنى ثقة للكشف عن الوضع'
                        },
                        'minTrackingConfidence': {
                            'type': 'number',
                            'default': 0.7,
                            'minimum': 0,
                            'maximum': 1,
                            'description': 'أدنى ثقة لتتبع الوضع'
                        }
                    },
                    'description': 'إعدادات تقدير الوضع'
                },
                'camera': {
                    'type': 'object',
                    'properties': {
                        'width': {
                            'type': 'integer',
                            'default': 800,
                            'minimum': 100,
                            'maximum': 4096,
                            'description': 'عرض الصورة من الكاميرا'
                        },
                        'height': {
                            'type': 'integer',
                            'default': 600,
                            'minimum': 100,
                            'maximum': 2160,
                            'description': 'ارتفاع الصورة من الكاميرا'
                        }
                    },
                    'description': 'إعدادات الكاميرا'
                },
                'attentionDecrementFactor': {
                    'type': 'integer',
                    'default': 5,
                    'minimum': 1,
                    'description': 'عامل تقليل الانتباه عند تشتيت الانتباه'
                },
                'attentionIncrementFactor': {
                    'type': 'integer',
                    'default': 1,
                    'minimum': 1,
                    'description': 'عامل زيادة الانتباه عند التركيز'
                },
                'noFaceDecrementFactor': {
                    'type': 'integer',
                    'default': 3,
                    'minimum': 1,
                    'description': 'عامل تقليل الانتباه عند عدم الكشف عن وجه'
                },
                'alerts': {
                    'type': 'object',
                    'properties': {
                        'head': {
                            'type': 'object',
                            'properties': {
                                'upThreshold': {
                                    'type': 'number',
                                    'default': -0.5,
                                    'minimum': -1,
                                    'maximum': 1,
                                    'description': 'عازل لالتقاط حركة الرأس للأعلى'
                                },
                                'downThreshold': {
                                    'type': 'number',
                                    'default': 0.5,
                                    'minimum': 0.0,
                                    'maximum': 1.0,
                                    'description': 'عازل لحركة الرأس لأسفل'
                                },
                                'lateralThreshold': {
                                    'type': 'number',
                                    'default': 15,
                                    'minimum': 0,
                                    'maximum': 180,
                                    'description': 'عازل لحركة الرأس الجانبية'
                                },
                                'duration': {
                                    'type': 'integer',
                                    'default': 3000,
                                    'minimum': 100,
                                    'description': 'المدة (بـ ms) قبل إطلاق التنبيه'
                                },
                                'enabled': {
                                    'type': 'object',
                                    'properties': {
                                        'up': {
                                            'type': 'boolean',
                                            'default': True,
                                            'description': 'تفعيل تنبيه الحركة للأعلى'
                                        },
                                        'down': {
                                            'type': 'boolean',
                                            'default': True,
                                            'description': 'تفعيل تنبيه الحركة لأسفل'
                                        },
                                        'left': {
                                            'type': 'boolean',
                                            'default': True,
                                            'description': 'تفعيل تنبيه الحركة لليسار'
                                        },
                                        'right': {
                                            'type': 'boolean',
                                            'default': True,
                                            'description': 'تفعيل تنبيه الحركة لليمين'
                                        },
                                        'forward': {
                                            'type': 'boolean',
                                            'default': True,
                                            'description': 'تفعيل تنبيه الحركة للأمام'
                                        }
                                    },
                                    'description': 'اتجاهات التنبيه المفعلة'
                                },
                                'detectTurnOnly': {
                                    'type': 'boolean',
                                    'default': True,
                                    'description': 'التقاط الحركة عند دوران الرأس فقط'
                                }
                            },
                            'description': 'إعدادات تنبيهات حركة الرأس'
                        },
                        'mouth': {
                            'type': 'object',
                            'properties': {
                                'threshold': {
                                    'type': 'number',
                                    'default': 0.05,
                                    'minimum': -1.00,
                                    'maximum': 1.00,
                                    'description': 'عازل لكشف فتح الفم'
                                },
                                'duration': {
                                    'type': 'integer',
                                    'default': 3000,
                                    'minimum': 100,
                                    'description': 'المدة (بـ ms) قبل إطلاق التنبيه'
                                },
                                'enabled': {
                                    'type': 'boolean',
                                    'default': True,
                                    'description': 'تفعيل تنبيه فتح الفم'
                                }
                            },
                            'description': 'إعدادات تنبيهات حركة الفم'
                        },
                        'gaze': {
                            'type': 'object',
                            'properties': {
                                'duration': {
                                    'type': 'integer',
                                    'default': 3000,
                                    'minimum': 100,
                                    'description': 'المدة (بـ ms) قبل إطلاق تنبيه نظرة العين'
                                },
                                'enabled': {
                                    'type': 'boolean',
                                    'default': True,
                                    'description': 'تفعيل تنبيه نظرة العين'
                                }
                            },
                            'description': 'إعدادات تنبيهات نظرة العين'
                        },
                        'headPose': {
                            'type': 'object',
                            'properties': {
                                'neutralRange': {
                                    'type': 'number',
                                    'default': 5,
                                    'description': 'النطاق المحايد لحركة الرأس'
                                },
                                'smoothingFrames': {
                                    'type': 'integer',
                                    'default': 10,
                                    'description': 'عدد الإطارات لتنعيم الحركة'
                                },
                                'referenceFrames': {
                                    'type': 'integer',
                                    'default': 30,
                                    'description': 'عدد الإطارات المرجعية'
                                }
                            },
                            'description': 'إعدادات مؤشرات وضع الرأس'
                        }
                    },
                    'description': 'إعدادات نظام التنبيهات'
                },
                'sendDataInterval': {
                    'type': 'integer',
                    'default': 5000,
                    'minimum': 1000,
                    'description': 'المدة (بـ ms) قبل إرسال البيانات إلى قاعدة البيانات'
                },
                'maxAlerts': {
                    'type': 'integer',
                    'default': 10,
                    'minimum': 1,
                    'description': 'العدد الأقصى للتنبيهات خلال هذه المدة'
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
                        "upThreshold": -0.5,
                        "downThreshold": 0.5,
                        "lateralThreshold": 15,
                        "duration": 3000,
                        "enabled": {
                            "up": True,
                            "down": True,
                            "left": True,
                            "right": True,
                            "forward": True
                        },
                        "detectTurnOnly": True
                    },
                    "mouth": {
                        "threshold": 0.05,
                        "duration": 3000,
                        "enabled": True
                    },
                    "gaze": {
                        "duration": 3000,
                        "enabled": True
                    },
                    "headPose": {
                        "neutralRange": 5,
                        "smoothingFrames": 10,
                        "referenceFrames": 30
                    }
                },
                "sendDataInterval": 5000,
                "maxAlerts": 10
            }
        }
    }],
    'responses': {
        200: {
            'description': 'تم تحديث الإعدادات بنجاح',
            'examples': {
                'application/json': {
                    'message': 'Configuration updated successfully',
                    'config_id': 1
                }
            }
        },
        400: {
            'description': 'إدخال غير صالح',
            'examples': {
                'application/json': {
                    'error': 'Error message describing the issue'
                }
            }
        },
        500: {
            'description': 'خطأ في الخادم',
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
    تحديث إعدادات النموذج بناءً على المعطيات الجديدة
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
    'description': 'إعادة تعيين الإعدادات إلى القيم الافتراضية',
    'responses': {
        200: {'description': 'تم إعادة التعيين إلى القيم الافتراضية'},
        500: {'description': 'خطأ في الخادم'}
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
    'description': 'استرجاع القيم الافتراضية للإعدادات (دون حفظها في قاعدة البيانات)',
    'responses': {
        200: {
            'description': 'القيم الافتراضية',
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
                            "upThreshold": -0.5,
                            "downThreshold": 0.5,
                            "lateralThreshold": 15,
                            "duration": 3000,
                            "enabled": {
                                "up": True,
                                "down": True,
                                "left": True,
                                "right": True,
                                "forward": True
                            },
                            "detectTurnOnly": True
                        },
                        "mouth": {
                            "threshold": 0.05,
                            "duration": 3000,
                            "enabled": True
                        },
                        "gaze": {
                            "duration": 3000,
                            "enabled": True
                        },
                        "headPose": {
                            "neutralRange": 5,
                            "smoothingFrames": 10,
                            "referenceFrames": 30
                        }
                    },
                    "sendDataInterval": 5000,
                    "maxAlerts": 10
                }
            }
        },
        500: {'description': 'خطأ في الخادم'}
    }
})
def get_default_config():
    try:
        default_config = service.get_default_config()
        # إزالة الحقول التي ليست ضرورية في الرد مثل id و updated_at
        default_config.pop("id", None)
        default_config.pop("updated_at", None)
        return jsonify(default_config), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

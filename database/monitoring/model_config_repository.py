from datetime import datetime
from database.connection import get_db_connection
from psycopg.errors import UndefinedTable
from typing import Dict, Optional

class ModelConfigRepository:
    def __init__(self):
        pass  # لا نحتاج لـ db_url لأننا نستخدم get_db_connection مباشرة

    def _convert_to_model(self, row_dict: Dict) -> Dict:
        """تحويل قاموس الصف إلى الهيكل المطلوب"""
        if not row_dict:
            return None
            
        return {
            "id": row_dict["id"],
            "updated_at": row_dict["updated_at"],
            "faceMeshOptions": {
                "maxNumFaces": row_dict["face_mesh_max_num_faces"],
                "refineLandmarks": row_dict["face_mesh_refine_landmarks"],
                "minDetectionConfidence": float(row_dict["face_mesh_min_detection_confidence"]),
                "minTrackingConfidence": float(row_dict["face_mesh_min_tracking_confidence"])
            },
            "poseOptions": {
                "modelComplexity": row_dict["pose_model_complexity"],
                "smoothLandmarks": row_dict["pose_smooth_landmarks"],
                "enableSegmentation": row_dict["pose_enable_segmentation"],
                "smoothSegmentation": row_dict["pose_smooth_segmentation"],
                "minDetectionConfidence": float(row_dict["pose_min_detection_confidence"]),
                "minTrackingConfidence": float(row_dict["pose_min_tracking_confidence"])
            },
            "camera": {
                "width": row_dict["camera_width"],
                "height": row_dict["camera_height"]
            },
            "attentionDecrementFactor": row_dict["attention_decrement_factor"],
            "attentionIncrementFactor": row_dict["attention_increment_factor"],
            "noFaceDecrementFactor": row_dict["no_face_decrement_factor"],
            "alerts": {
                "head": {
                    "upThreshold": float(row_dict["head_up_threshold"]),
                    "downThreshold": float(row_dict["head_down_threshold"]),
                    "lateralThreshold": float(row_dict["head_lateral_threshold"]),
                    "duration": row_dict["head_duration"],
                    "enabled": {
                        "up": row_dict["head_enabled_up"],
                        "down": row_dict["head_enabled_down"],
                        "left": row_dict["head_enabled_left"],
                        "right": row_dict["head_enabled_right"],
                        "forward": row_dict["head_enabled_forward"]
                    }
                },
                "mouth": {
                    "threshold": float(row_dict["mouth_threshold"]),
                    "duration": row_dict["mouth_duration"],
                    "enabled": row_dict["mouth_enabled"]
                },
                "gaze": {
                    "duration": row_dict["gaze_duration"],
                    "enabled": row_dict["gaze_enabled"]
                },
                "headPose": {
                    "neutralRange": row_dict["headpose_neutral_range"],
                    "smoothingFrames": row_dict["headpose_smoothing_frames"],
                    "referenceFrames": row_dict["headpose_reference_frames"]
                }
            },
            # إعدادات إضافية
            "sendDataInterval": row_dict["send_data_interval"],   # المدة قبل إرسال البيانات لقاعدة البيانات (بـ ms)
            "maxAlerts": row_dict["max_alerts"]                     # عدد التنبيهات الافتراضي خلال هذه المدة
        }

    def get_config(self, config_id: int) -> Optional[Dict]:
        """استرجاع إعدادات محددة باستخدام الـ ID"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT * FROM model_config WHERE id = %s",
                        (config_id,)
                    )
                    row = cursor.fetchone()
                    return self._convert_to_model(row)
        except UndefinedTable:
            raise Exception("Model config table does not exist")
        except Exception as e:
            raise Exception(f"Failed to get config: {str(e)}")

    def get_active_config(self) -> Optional[Dict]:
        """استرجاع الإعدادات النشطة حالياً"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT * FROM model_config ORDER BY updated_at DESC LIMIT 1"
                    )
                    row = cursor.fetchone()
                    return self._convert_to_model(row)
        except UndefinedTable:
            raise Exception("Model config table does not exist")
        except Exception as e:
            raise Exception(f"Failed to get active config: {str(e)}")

    def update_config(self, config_id: int, config_data: Dict) -> Dict:
        """تحديث الإعدادات في قاعدة البيانات"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE model_config SET
                            face_mesh_max_num_faces = %(maxNumFaces)s,
                            face_mesh_refine_landmarks = %(refineLandmarks)s,
                            face_mesh_min_detection_confidence = %(fm_minDetectionConfidence)s,
                            face_mesh_min_tracking_confidence = %(fm_minTrackingConfidence)s,
                            pose_model_complexity = %(modelComplexity)s,
                            pose_smooth_landmarks = %(smoothLandmarks)s,
                            pose_enable_segmentation = %(enableSegmentation)s,
                            pose_smooth_segmentation = %(smoothSegmentation)s,
                            pose_min_detection_confidence = %(pose_minDetectionConfidence)s,
                            pose_min_tracking_confidence = %(pose_minTrackingConfidence)s,
                            camera_width = %(width)s,
                            camera_height = %(height)s,
                            attention_decrement_factor = %(attentionDecrementFactor)s,
                            attention_increment_factor = %(attentionIncrementFactor)s,
                            no_face_decrement_factor = %(noFaceDecrementFactor)s,
                            head_up_threshold = %(upThreshold)s,
                            head_down_threshold = %(downThreshold)s,
                            head_lateral_threshold = %(lateralThreshold)s,
                            head_duration = %(headDuration)s,
                            head_enabled_up = %(upEnabled)s,
                            head_enabled_down = %(downEnabled)s,
                            head_enabled_left = %(leftEnabled)s,
                            head_enabled_right = %(rightEnabled)s,
                            head_enabled_forward = %(forwardEnabled)s,
                            mouth_threshold = %(mouthThreshold)s,
                            mouth_duration = %(mouthDuration)s,
                            mouth_enabled = %(mouthEnabled)s,
                            gaze_duration = %(gazeDuration)s,
                            gaze_enabled = %(gazeEnabled)s,
                            headpose_neutral_range = %(headPoseNeutralRange)s,
                            headpose_smoothing_frames = %(headPoseSmoothingFrames)s,
                            headpose_reference_frames = %(headPoseReferenceFrames)s,
                            send_data_interval = %(sendDataInterval)s,
                            max_alerts = %(maxAlerts)s
                        WHERE id = %(config_id)s
                        RETURNING *;
                        """,
                        {
                            "config_id": config_id,
                            # faceMeshOptions
                            "maxNumFaces": config_data["faceMeshOptions"]["maxNumFaces"],
                            "refineLandmarks": config_data["faceMeshOptions"]["refineLandmarks"],
                            "fm_minDetectionConfidence": config_data["faceMeshOptions"]["minDetectionConfidence"],
                            "fm_minTrackingConfidence": config_data["faceMeshOptions"]["minTrackingConfidence"],
                            # poseOptions
                            "modelComplexity": config_data["poseOptions"]["modelComplexity"],
                            "smoothLandmarks": config_data["poseOptions"]["smoothLandmarks"],
                            "enableSegmentation": config_data["poseOptions"]["enableSegmentation"],
                            "smoothSegmentation": config_data["poseOptions"]["smoothSegmentation"],
                            "pose_minDetectionConfidence": config_data["poseOptions"]["minDetectionConfidence"],
                            "pose_minTrackingConfidence": config_data["poseOptions"]["minTrackingConfidence"],
                            # camera
                            "width": config_data["camera"]["width"],
                            "height": config_data["camera"]["height"],
                            # عوامل الانتباه
                            "attentionDecrementFactor": config_data["attentionDecrementFactor"],
                            "attentionIncrementFactor": config_data["attentionIncrementFactor"],
                            "noFaceDecrementFactor": config_data["noFaceDecrementFactor"],
                            # alerts -> head
                            "upThreshold": config_data["alerts"]["head"]["upThreshold"],
                            "downThreshold": config_data["alerts"]["head"]["downThreshold"],
                            "lateralThreshold": config_data["alerts"]["head"]["lateralThreshold"],
                            "headDuration": config_data["alerts"]["head"]["duration"],
                            "upEnabled": config_data["alerts"]["head"]["enabled"]["up"],
                            "downEnabled": config_data["alerts"]["head"]["enabled"]["down"],
                            "leftEnabled": config_data["alerts"]["head"]["enabled"]["left"],
                            "rightEnabled": config_data["alerts"]["head"]["enabled"]["right"],
                            "forwardEnabled": config_data["alerts"]["head"]["enabled"]["forward"],
                            # alerts -> mouth
                            "mouthThreshold": config_data["alerts"]["mouth"]["threshold"],
                            "mouthDuration": config_data["alerts"]["mouth"]["duration"],
                            "mouthEnabled": config_data["alerts"]["mouth"]["enabled"],
                            # alerts -> gaze
                            "gazeDuration": config_data["alerts"]["gaze"]["duration"],
                            "gazeEnabled": config_data["alerts"]["gaze"]["enabled"],
                            # alerts -> headPose
                            "headPoseNeutralRange": config_data["alerts"]["headPose"]["neutralRange"],
                            "headPoseSmoothingFrames": config_data["alerts"]["headPose"]["smoothingFrames"],
                            "headPoseReferenceFrames": config_data["alerts"]["headPose"]["referenceFrames"],
                            # إعدادات إضافية
                            "sendDataInterval": config_data["sendDataInterval"],
                            "maxAlerts": config_data["maxAlerts"]
                        }
                    )
                    updated_row = cursor.fetchone()
                    conn.commit()
                    if not updated_row:
                        raise ValueError("Config not found or no changes made")
                    return self._convert_to_model(updated_row)
        except UndefinedTable as e:
            conn.rollback()
            raise Exception("Model config table does not exist")
        except Exception as e:
            conn.rollback()
            raise Exception(f"Failed to update config: {str(e)}")

    def get_default_config(self) -> Dict:
        """الحصول على الإعدادات الافتراضية طبقاً للمعطيات الجديدة"""
        return {
            "id": 1,  # الافتراض أن الإعداد الافتراضي يحمل ID=1
            "faceMeshOptions": {
                "maxNumFaces": 1,
                "refineLandmarks": True,
                "minDetectionConfidence": 0.7,
                "minTrackingConfidence": 0.7,
            },
            "poseOptions": {
                "modelComplexity": 1,
                "smoothLandmarks": True,
                "enableSegmentation": False,
                "smoothSegmentation": False,
                "minDetectionConfidence": 0.7,
                "minTrackingConfidence": 0.7,
            },
            "camera": {
                "width": 800,
                "height": 600,
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
                        "forward": True,
                    },
                },
                "mouth": {
                    "threshold": 0.05,
                    "duration": 3000,
                    "enabled": True,
                },
                "gaze": {
                    "duration": 3000,
                    "enabled": True,
                },
                "headPose": {
                    "neutralRange": 5,
                    "smoothingFrames": 10,
                    "referenceFrames": 30,
                },
            },
            # إعدادات إضافية:
            "sendDataInterval": 5000,  # المدة (بـ ms) قبل إرسال البيانات إلى قاعدة البيانات
            "maxAlerts": 10          # عدد التنبيهات الافتراضي خلال هذه المدة
            ,
            "updated_at": datetime.now()
        }

    def reset_to_default(self) -> Dict:
        """إعادة تعيين الإعدادات إلى القيم الافتراضية"""
        default_config = self.get_default_config()
        return self.update_config(default_config["id"], default_config)

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
                    "downThreshold": float(row_dict["head_down_threshold"]),
                    "lateralThreshold": float(row_dict["head_lateral_threshold"]),
                    "duration": row_dict["head_duration"],
                    "enabled": {
                        "down": row_dict["head_enabled_down"],
                        "left": row_dict["head_enabled_left"],
                        "right": row_dict["head_enabled_right"]
                    },
                    "detectTurnOnly": row_dict["head_detect_turn_only"]
                },
                "mouth": {
                    "threshold": float(row_dict["mouth_threshold"]),
                    "duration": row_dict["mouth_duration"],
                    "enabled": row_dict["mouth_enabled"]
                }
            }
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
        """تحديث الإعدادات"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE model_config SET
                            face_mesh_max_num_faces = %(maxNumFaces)s,
                            face_mesh_refine_landmarks = %(refineLandmarks)s,
                            face_mesh_min_detection_confidence = %(minDetectionConfidence)s,
                            face_mesh_min_tracking_confidence = %(minTrackingConfidence)s,
                            pose_model_complexity = %(modelComplexity)s,
                            pose_smooth_landmarks = %(smoothLandmarks)s,
                            pose_enable_segmentation = %(enableSegmentation)s,
                            pose_smooth_segmentation = %(smoothSegmentation)s,
                            pose_min_detection_confidence = %(minDetectionConfidence)s,
                            pose_min_tracking_confidence = %(minTrackingConfidence)s,
                            camera_width = %(width)s,
                            camera_height = %(height)s,
                            attention_decrement_factor = %(attentionDecrementFactor)s,
                            attention_increment_factor = %(attentionIncrementFactor)s,
                            no_face_decrement_factor = %(noFaceDecrementFactor)s,
                            head_down_threshold = %(downThreshold)s,
                            head_lateral_threshold = %(lateralThreshold)s,
                            head_duration = %(duration)s,
                            head_enabled_down = %(downEnabled)s,
                            head_enabled_left = %(leftEnabled)s,
                            head_enabled_right = %(rightEnabled)s,
                            head_detect_turn_only = %(detectTurnOnly)s,
                            mouth_threshold = %(threshold)s,
                            mouth_duration = %(duration)s,
                            mouth_enabled = %(enabled)s
                        WHERE id = %(config_id)s
                        RETURNING *;
                        """,
                        {
                            "config_id": config_id,
                            "maxNumFaces": config_data["faceMeshOptions"]["maxNumFaces"],
                            "refineLandmarks": config_data["faceMeshOptions"]["refineLandmarks"],
                            "minDetectionConfidence": config_data["faceMeshOptions"]["minDetectionConfidence"],
                            "minTrackingConfidence": config_data["faceMeshOptions"]["minTrackingConfidence"],
                            "modelComplexity": config_data["poseOptions"]["modelComplexity"],
                            "smoothLandmarks": config_data["poseOptions"]["smoothLandmarks"],
                            "enableSegmentation": config_data["poseOptions"]["enableSegmentation"],
                            "smoothSegmentation": config_data["poseOptions"]["smoothSegmentation"],
                            "minDetectionConfidence": config_data["poseOptions"]["minDetectionConfidence"],
                            "minTrackingConfidence": config_data["poseOptions"]["minTrackingConfidence"],
                            "width": config_data["camera"]["width"],
                            "height": config_data["camera"]["height"],
                            "attentionDecrementFactor": config_data["attentionDecrementFactor"],
                            "attentionIncrementFactor": config_data["attentionIncrementFactor"],
                            "noFaceDecrementFactor": config_data["noFaceDecrementFactor"],
                            "downThreshold": config_data["alerts"]["head"]["downThreshold"],
                            "lateralThreshold": config_data["alerts"]["head"]["lateralThreshold"],
                            "duration": config_data["alerts"]["head"]["duration"],
                            "downEnabled": config_data["alerts"]["head"]["enabled"]["down"],
                            "leftEnabled": config_data["alerts"]["head"]["enabled"]["left"],
                            "rightEnabled": config_data["alerts"]["head"]["enabled"]["right"],
                            "detectTurnOnly": config_data["alerts"]["head"]["detectTurnOnly"],
                            "threshold": config_data["alerts"]["mouth"]["threshold"],
                            "duration": config_data["alerts"]["mouth"]["duration"],
                            "enabled": config_data["alerts"]["mouth"]["enabled"]
                        }
                    )
                    updated_row = cursor.fetchone()
                    conn.commit()
                    if not updated_row:
                        raise ValueError("Config not found or no changes made")
                    return self._convert_to_model(updated_row)
        except UndefinedTable:
            conn.rollback()
            raise Exception("Model config table does not exist")
        except Exception as e:
            conn.rollback()
            raise Exception(f"Failed to update config: {str(e)}")

    def reset_to_default(self) -> Dict:
        """إعادة تعيين الإعدادات إلى القيم الافتراضية"""
        default_config = self.get_default_config()
        return self.update_config(default_config["id"], default_config)

    def get_default_config(self) -> Dict:
        """الحصول على الإعدادات الافتراضية"""
        return {
            "id": 1,  # Assuming default config has ID=1
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
                    "downThreshold": 0.8,
                    "lateralThreshold": 0.7,
                    "duration": 3000,
                    "enabled": {
                        "down": True,
                        "left": False,
                        "right": False,
                    },
                    "detectTurnOnly": True,
                },
                "mouth": {
                    "threshold": 0.01,
                    "duration": 10000,
                    "enabled": True,
                }
            },
            "updated_at": datetime.now()
        }
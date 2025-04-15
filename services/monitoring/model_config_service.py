from typing import Dict, Optional
from database.monitoring.model_config_repository import ModelConfigRepository
from psycopg.errors import UndefinedTable
from datetime import datetime

class ModelConfigService:
    def __init__(self):
        """Initialize the service with a repository instance"""
        self.repository = ModelConfigRepository()

    def get_current_config(self) -> Dict:
        """
        Get the currently active configuration
        
        Returns:
            Dict: Current model configuration as a structured dictionary
            
        Raises:
            Exception: If there's a database error
        """
        try:
            config = self.repository.get_active_config()
            if not config:
                return self._create_default_config()
            return config
        except UndefinedTable:
            # If table doesn't exist, return default config
            return self.get_default_config()
        except Exception as e:
            raise Exception(f"Failed to get current config: {str(e)}")

    def update_config(self, config_id: int, config_data: Dict) -> Dict:
        """
        Update model configuration
        
        Args:
            config_id (int): ID of the record to update
            config_data (Dict): New configuration data
            
        Returns:
            Dict: Updated configuration
            
        Raises:
            ValueError: If data is invalid
            Exception: If there's a database error
        """
        try:
            self._validate_config(config_data)
            return self.repository.update_config(config_id, config_data)
        except ValueError as ve:
            raise ValueError(f"Invalid data: {str(ve)}")
        except Exception as e:
            raise Exception(f"Failed to update config: {str(e)}")

    def reset_to_default(self) -> Dict:
        """
        Reset configuration to default values
        
        Returns:
            Dict: Default configuration after update
            
        Raises:
            Exception: If there's a database error
        """
        try:
            return self.repository.reset_to_default()
        except Exception as e:
            raise Exception(f"Failed to reset to default: {str(e)}")

    def get_default_config(self) -> Dict:
        """
        Get default configuration (without saving to database)
        
        Returns:
            Dict: Default configuration
        """
        return self.repository.get_default_config()

    def _validate_config(self, config_data: Dict):
        """
        Validate configuration data
        
        Args:
            config_data (Dict): Configuration data to validate
            
        Raises:
            ValueError: If data is invalid
        """
        if not isinstance(config_data, dict):
            raise ValueError("Configuration data must be a dictionary")
            
        # Validate Face Mesh settings
        face_mesh = config_data.get("faceMeshOptions", {})
        if not 1 <= face_mesh.get("maxNumFaces", 0) <= 10:
            raise ValueError("Number of faces must be between 1 and 10")
        if not 0 <= face_mesh.get("minDetectionConfidence", -1) <= 1:
            raise ValueError("Detection confidence must be between 0 and 1")
        if not 0 <= face_mesh.get("minTrackingConfidence", -1) <= 1:
            raise ValueError("Tracking confidence must be between 0 and 1")

        # Validate Pose settings
        pose = config_data.get("poseOptions", {})
        if pose.get("modelComplexity", 0) not in [0, 1, 2]:
            raise ValueError("Model complexity must be 0, 1, or 2")
        if not 0 <= pose.get("minDetectionConfidence", -1) <= 1:
            raise ValueError("Detection confidence must be between 0 and 1")
        if not 0 <= pose.get("minTrackingConfidence", -1) <= 1:
            raise ValueError("Tracking confidence must be between 0 and 1")

        # Validate Camera settings
        camera = config_data.get("camera", {})
        if not 100 <= camera.get("width", 0) <= 4096:
            raise ValueError("Camera width must be between 100 and 4096")
        if not 100 <= camera.get("height", 0) <= 2160:
            raise ValueError("Camera height must be between 100 and 2160")

        # Validate attention factors
        if config_data.get("attentionDecrementFactor", 0) <= 0:
            raise ValueError("Attention decrement factor must be positive")
        if config_data.get("attentionIncrementFactor", 0) <= 0:
            raise ValueError("Attention increment factor must be positive")
        if config_data.get("noFaceDecrementFactor", 0) <= 0:
            raise ValueError("No face decrement factor must be positive")

        # Validate alert settings
        alerts = config_data.get("alerts", {})
        head = alerts.get("head", {})
        if not 0 <= head.get("downThreshold", -1) <= 1:
            raise ValueError("Head down threshold must be between 0 and 1")
        if not 0 <= head.get("lateralThreshold", -1) <= 180:
            raise ValueError("Lateral threshold must be between 0 and 1")
        if head.get("duration", 0) <= 0:
            raise ValueError("Alert duration must be positive")

        mouth = alerts.get("mouth", {})
        if not 0 <= mouth.get("threshold", -1) <= 1:
            raise ValueError("Mouth threshold must be between 0 and 1")
        if mouth.get("duration", 0) <= 0:
            raise ValueError("Alert duration must be positive")

    def _create_default_config(self) -> Dict:
        """
        Create default configuration and save to database
        
        Returns:
            Dict: Default configuration
        """
        default_config = self.get_default_config()
        return self.repository.update_config(default_config["id"], default_config)
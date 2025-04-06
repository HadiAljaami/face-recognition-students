from typing import Dict, List, Optional
from database.monitoring.alert_type_repository import AlertTypeRepository

class AlertTypeService:
    
    def __init__(self, repo: Optional[AlertTypeRepository] = None):
        self.repo = repo or AlertTypeRepository()

    def create_alert_type(self, type_name: str) -> Dict:
        """Create new alert type with validation"""
        if not type_name or len(type_name.strip()) < 2:
            raise ValueError("Type name must be at least 2 characters")
        
        try:
            return self.repo.create(type_name.strip())
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Service error: {str(e)}")

    def get_alert_type(self, type_id: int) -> Optional[Dict]:
        """Get single alert type"""
        try:
            return self.repo.get_by_id(type_id)
        except Exception as e:
            raise Exception(f"Service error: {str(e)}")

    def get_all_alert_types(self) -> List[Dict]:
        """List all alert types"""
        try:
            return self.repo.get_all()
        except Exception as e:
            raise Exception(f"Service error: {str(e)}")

    def update_alert_type(self, type_id: int, new_name: str) -> Dict:
        """Update existing alert type"""
        if not new_name or len(new_name.strip()) < 2:
            raise ValueError("Type name must be at least 2 characters")
        
        try:
            return self.repo.update(type_id, new_name.strip())
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Service error: {str(e)}")

    def delete_alert_type(self, type_id: int) -> bool:
        """Delete alert type if not in use"""
        try:
            return self.repo.delete(type_id)
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Service error: {str(e)}")
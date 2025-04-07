from typing import Dict, List, Optional
from database.monitoring.alert_repository import AlertRepository
from database.monitoring.alert_type_repository import AlertTypeRepository
from datetime import time

class AlertService:
    
    def __init__(self, 
                 alert_repo: Optional[AlertRepository] = None,
                 alert_type_repo: Optional[AlertTypeRepository] = None):
        self.alert_repo = alert_repo or AlertRepository()
        self.alert_type_repo = alert_type_repo or AlertTypeRepository()

    def create_alert(self, exam_id: int, student_id: int, device_id: int,
                    alert_type: int, message: str = None) -> Dict:
        """Create new alert with validation"""
        if not all([exam_id, student_id, device_id, alert_type]):
            raise ValueError("All required fields must be provided")
        
        # Verify alert type exists
        if not self.alert_type_repo.get_by_id(alert_type):
            raise ValueError("Invalid alert type")
        
        try:
            return self.alert_repo.create(
                exam_id=exam_id,
                student_id=student_id,
                device_id=device_id,
                alert_type=alert_type,
                message=message
            )
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Service error: {str(e)}")

    def get_alert_devices(
        self,
        center_id: Optional[int] = None,
        room_number: Optional[str] = None,
        exam_date: Optional[str] = None,
        start_time: Optional[time] = None,
        end_time: Optional[time] = None
    ) -> List[Dict]:
        """
        Get devices with cheating alerts
        Filters are optional - if None, that filter is not applied
        """
        try:
            return self.alert_repo.get_alert_devices(
                center_id=center_id,
                room_number=room_number,
                exam_date=exam_date,
                start_time=start_time,
                end_time=end_time
            )
        except Exception as e:
            raise Exception(f"Service error: {str(e)}")

    def get_and_mark_alerts(self, device_id: int, student_id: int, exam_id: int):
            """
            Get alert messages and mark unread ones as read.
            The read status is sent before updating.
            """
            # Step 1: Fetch all alerts (including is_read status)
            alerts = self.alert_repo.get_alert_details(device_id, student_id, exam_id)

            # Step 2: Update unread alerts to is_read = true
            self.alert_repo.mark_alerts_as_read(device_id, student_id, exam_id)

            return alerts

    # def get_alert_details(
    #     self,
    #     device_id: int,
    #     student_id: int,
    #     exam_id: int
    # ) -> Dict:
    #     """
    #     Get alert details and mark them as read
    #     Returns: {
    #         'device_id': int,
    #         'student_id': int,
    #         'exam_id': int,
    #         'alerts': List[Dict]  # list of alert details
    #     }
    #     """
    #     try:
    #         # Get the alerts first
    #         alerts = self.alert_repo.get_alert_details(device_id, student_id, exam_id)
            
    #         # Mark them as read
    #         self.alert_repo.mark_alerts_as_read(device_id, student_id, exam_id)
            
    #         return {
    #             'device_id': device_id,
    #             'student_id': student_id,
    #             'exam_id': exam_id,
    #             'alerts': alerts
    #         }
    #     except Exception as e:
    #         raise Exception(f"Service error: {str(e)}")

    # def get_alert(self, alert_id: int) -> Optional[Dict]:
    #     """Get alert details"""
    #     try:
    #         alert = self.alert_repo.get_by_id(alert_id)
    #         if not alert:
    #             raise ValueError("Alert not found")
    #         return alert
    #     except Exception as e:
    #         raise Exception(f"Service error: {str(e)}")

    # def get_alerts(self, exam_id: int = None, student_id: int = None,
    #               is_read: bool = None, limit: int = 100) -> List[Dict]:
    #     """Get filtered alerts"""
    #     filters = {}
    #     if exam_id:
    #         filters['exam_id'] = exam_id
    #     if student_id:
    #         filters['student_id'] = student_id
    #     if is_read is not None:
    #         filters['is_read'] = is_read
            
    #     try:
    #         alerts = self.alert_repo.get_all(filters)
    #         return alerts[:limit]
    #     except Exception as e:
    #         raise Exception(f"Service error: {str(e)}")

    # def mark_alerts_read(self, alert_ids: List[int]) -> int:
    #     """Mark alerts as read"""
    #     if not alert_ids:
    #         return 0
            
    #     try:
    #         return self.alert_repo.mark_as_read(alert_ids)
    #     except Exception as e:
    #         raise Exception(f"Service error: {str(e)}")

    # def delete_alerts(self, alert_ids: List[int]) -> int:
    #     """Delete alerts"""
    #     if not alert_ids:
    #         raise ValueError("No alert IDs provided")
            
    #     try:
    #         return self.alert_repo.delete(alert_ids)
    #     except Exception as e:
    #         raise Exception(f"Service error: {str(e)}")
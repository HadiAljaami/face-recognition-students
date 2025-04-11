# services/devices_service.py
from typing import Optional, List, Dict
from database.devices_repository import DevicesRepository
import secrets

class DevicesService:
    
    def __init__(self, repository: DevicesRepository):
        self.repository = repository

    def generate_device_token(self) -> str:
        """توليد توكن فريد للجهاز"""
        return secrets.token_hex(32)

    def register_device(self, device_number: int, room_number: str, center_id: int) -> Dict:
        """تسجيل جهاز جديد مع توليد توكن"""
        device_token = self.generate_device_token()
        return self.repository.add_device(
            device_number=device_number,
            device_token=device_token,
            room_number=room_number,
            center_id=center_id
        )

    def update_device(self, device_id: int, **kwargs) -> bool:
        """تحديث بيانات الجهاز"""
        return self.repository.update_device(device_id, **kwargs)

    def delete_device(self, device_id: int) -> bool:
        """حذف جهاز"""
        return self.repository.delete_device(device_id)

    def get_device_by_number(self, device_number: int) -> Optional[Dict]:
        """الحصول على جهاز بواسطة رقم الجهاز"""
        return self.repository.get_device_by_number(device_number)
    
    def get_device_by_id(self, device_id: int) -> Optional[Dict]:
        """الحصول على جهاز بواسطة رقم الجهاز"""
        return self.repository.get_device_by_id(device_id)

    def get_all_devices(self, filters: Optional[Dict] = None) -> List[Dict]:
        """الحصول على جميع الأجهزة مع فلترة اختيارية"""
        center_id = filters.get('center_id') if filters else None
        room_number = filters.get('room_number') if filters else None
        return self.repository.get_all_devices(center_id=center_id, room_number=room_number)

    def toggle_device_status(self, device_id: int) -> Optional[Dict]:
        """تبديل حالة الجهاز"""
        return self.repository.toggle_device_status(device_id)

    def validate_device_token(self, device_token: str) -> bool:
        """التحقق من صحة توكن الجهاز"""
        device = self.repository.get_device_by_token(device_token)
        return device is not None and device['status'] == 1

    def refresh_device_token(self, device_id: int) -> Optional[str]:
        """تحديث توكن الجهاز"""
        new_token = self.generate_device_token()
        if self.repository.update_device(device_id, device_token=new_token):
            return new_token
        return None
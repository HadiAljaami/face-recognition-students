# services/centers_service.py
from database.centers_repository import CentersRepository

class CentersService:
    def __init__(self):
        self.repository = CentersRepository()

    def get_all_centers(self):
        """Get all exam centers"""
        return self.repository.get_all_centers()

    def get_center_by_id(self, center_id):
        """Get a single center by its ID"""
        return self.repository.get_center_by_id(center_id)

    def add_center(self, center_name, status=1):
        """
        Add a new exam center
        Args:
            center_name: Name of the center (must be unique)
            status: Status of the center (1 for active, 0 for inactive)
        """
        return self.repository.add_center(center_name, status)

    def update_center(self, center_id, center_name=None, status=None):
        """
        Update an existing exam center
        Args:
            center_id: ID of the center to update
            center_name: New name for the center (optional)
            status: New status for the center (optional)
        """
        return self.repository.update_center(center_id, center_name, status)

    def delete_center(self, center_id):
        """Delete an exam center by its ID"""
        return self.repository.delete_center(center_id)

    def search_centers_by_name(self, name):
        """Search centers by name (case-insensitive partial match)"""
        return self.repository.search_centers_by_name(name)
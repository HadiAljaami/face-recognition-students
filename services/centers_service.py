# services/centers_service.py
from database.centers_repository import CentersRepository

class CentersService:
    def __init__(self):
        self.repository = CentersRepository()

    def get_all_centers(self):
        return self.repository.get_all_centers()

    def get_center_by_id(self, center_id):
        return self.repository.get_center_by_id(center_id)

    def add_center(self, center_code, center_name, status=1):
        return self.repository.add_center(center_code, center_name, status)

    def update_center(self, center_id, center_code=None, center_name=None, status=None):
        return self.repository.update_center(center_id, center_code, center_name, status)

    def delete_center(self, center_id):
        return self.repository.delete_center(center_id)

    def search_centers_by_name(self, name):
        return self.repository.search_centers_by_name(name)

    def search_centers_by_code(self, code):
        return self.repository.search_centers_by_code(code)
# services/users_service.py
from database.users_repository import UsersRepository

class UsersService:
    def __init__(self):
        self.repository = UsersRepository()

    def verify_user(self, username, password):
        return self.repository.verify_user(username, password)
    
    def get_all_users(self):
        return self.repository.get_all_users()

    def get_user_by_id(self, user_id):
        return self.repository.get_user_by_id(user_id)

    def add_user(self, username, password, role):
        return self.repository.add_user(username, password, role)

    def update_user(self, user_id, username=None, password=None, role=None):
        return self.repository.update_user(user_id, username, password, role)

    def delete_user(self, user_id):
        return self.repository.delete_user(user_id)

    def search_users_by_username(self, username):
        return self.repository.search_users_by_username(username)
# routes/users_routes.py
from flask import Blueprint, request, jsonify
from services.users_service import UsersService
from flask_jwt_extended import create_access_token # dont delete !!!

users_bp = Blueprint('users', __name__)
service = UsersService()

@users_bp.route('/users', methods=['GET'])
def get_all_users():
    """
    Get all users
    ---
    tags:
      - Users
    responses:
      200:
        description: List of all users
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              username:
                type: string
              role:
                type: string
      500:
        description: Internal server error
    """
    try:
        users = service.get_all_users()
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    Get user by ID
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: User details
        schema:
          type: object
          properties:
            id:
              type: integer
            username:
              type: string
            role:
              type: string
      404:
        description: User not found
      500:
        description: Internal server error
    """
    try:
        user = service.get_user_by_id(user_id)
        if user:
            return jsonify(user)
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('/users', methods=['POST'])
def add_user():
    """
    Add a new user
    ---
    tags:
      - Users
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
            role:
              type: string
    responses:
      201:
        description: User added successfully
        schema:
          type: object
          properties:
            id:
              type: integer
            username:
              type: string
            role:
              type: string
      400:
        description: Invalid input
      500:
        description: Internal server error
    """
    try:
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password') or not data.get('role'):
            return jsonify({"error": "username, password, and role are required"}), 400


        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        role = data.get('role', '').strip()

        # تحقق من طول الحقول
        if len(username) > 20:
            return jsonify({"error": "Username must not exceed 50 characters"}), 400
        if len(password) > 20:
            return jsonify({"error": "Password must not exceed 255 characters"}), 400

        user = service.add_user(username=username, password=password, role=role)
        return jsonify(user), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """
    Update a user
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
            role:
              type: string
    responses:
      200:
        description: User updated successfully
        schema:
          type: object
          properties:
            id:
              type: integer
            username:
              type: string
            role:
              type: string
      400:
        description: Invalid input
      404:
        description: User not found
      500:
        description: Internal server error
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        role = data.get('role', '').strip()

        if len(username) > 20:
            return jsonify({"error": "Username must not exceed 20 characters"}), 400
        if len(password) > 20:
            return jsonify({"error": "Password must not exceed 20 characters"}), 400

        user = service.update_user(user_id=user_id, username=username, password=password, role=role)

        if user:
            return jsonify(user)
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    Delete a user
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: User deleted successfully
        schema:
          type: object
          properties:
            id:
              type: integer
            username:
              type: string
            role:
              type: string
      404:
        description: User not found
      500:
        description: Internal server error
    """
    try:
        user = service.delete_user(user_id)
        if user:
            return jsonify(user)
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('/users/search', methods=['GET'])
def search_users():
    """
    Search users by username
    ---
    tags:
      - Users
    parameters:
      - name: username
        in: query
        type: string
        required: true
    responses:
      200:
        description: List of users matching the search criteria
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              username:
                type: string
              role:
                type: string
      400:
        description: No search criteria provided
      500:
        description: Internal server error
    """
    try:
        username = request.args.get('username')
        if not username:
            return jsonify({"error": "Please provide username for search"}), 400

        users = service.search_users_by_username(username)
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# dont delete !!!
@users_bp.route('/login', methods=['POST'])
def login():
    """
    User login
    ---
    tags:
      - Users
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            access_token:
              type: string
      401:
        description: Invalid username or password
      500:
        description: Internal server error
    """
    try:
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({"error": "username and password are required"}), 400

        user = service.verify_user(data['username'], data['password'])
        if user:
            access_token = create_access_token(identity=user['username'])  # إنشاء token
            return jsonify({"access_token": access_token}), 200
        return jsonify({"error": "Invalid username or password"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

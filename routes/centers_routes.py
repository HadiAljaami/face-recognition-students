# routes/centers_routes.py
from flask import Blueprint, request, jsonify
from services.centers_service import CentersService

centers_bp = Blueprint('centers', __name__)
service = CentersService()

@centers_bp.route('/centers', methods=['GET'])
def get_all_centers():
    """
    Get all centers
    ---
    tags:
      - Centers
    responses:
      200:
        description: List of all centers
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              center_name:
                type: string
              status:
                type: integer
      500:
        description: Internal server error
    """
    try:
        centers = service.get_all_centers()
        return jsonify(centers)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@centers_bp.route('/centers/<int:center_id>', methods=['GET'])
def get_center(center_id):
    """
    Get center by ID
    ---
    tags:
      - Centers
    parameters:
      - name: center_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Center details
        schema:
          type: object
          properties:
            id:
              type: integer
            center_name:
              type: string
            status:
              type: integer
      404:
        description: Center not found
      500:
        description: Internal server error
    """
    try:
        center = service.get_center_by_id(center_id)
        if center:
            return jsonify(center)
        return jsonify({"error": "Center not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@centers_bp.route('/centers', methods=['POST'])
def add_center():
    """
    Add a new center
    ---
    tags:
      - Centers
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            center_name:
              type: string
            status:
              type: integer
    responses:
      201:
        description: Center added successfully
        schema:
          type: object
          properties:
            id:
              type: integer
            center_name:
              type: string
            status:
              type: integer
      400:
        description: Invalid input
      500:
        description: Internal server error
    """
    try:
        data = request.get_json()
        if not data or not data.get('center_name'):
            return jsonify({"error": "center_name is required"}), 400

        center = service.add_center(
            center_name=data['center_name'],
            status=data.get('status', 1)
        )
        return jsonify(center), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@centers_bp.route('/centers/<int:center_id>', methods=['PUT'])
def update_center(center_id):
    """
    Update a center
    ---
    tags:
      - Centers
    parameters:
      - name: center_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            center_name:
              type: string
            status:
              type: integer
    responses:
      200:
        description: Center updated successfully
        schema:
          type: object
          properties:
            id:
              type: integer
            center_name:
              type: string
            status:
              type: integer
      400:
        description: Invalid input
      404:
        description: Center not found
      500:
        description: Internal server error
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        center = service.update_center(
            center_id=center_id,
            center_name=data.get('center_name'),
            status=data.get('status')
        )
        if center:
            return jsonify(center)
        return jsonify({"error": "Center not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@centers_bp.route('/centers/<int:center_id>', methods=['DELETE'])
def delete_center(center_id):
    """
    Delete a center
    ---
    tags:
      - Centers
    parameters:
      - name: center_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Center deleted successfully
        schema:
          type: object
          properties:
            id:
              type: integer
            center_name:
              type: string
            status:
              type: integer
      404:
        description: Center not found
      500:
        description: Internal server error
    """
    try:
        center = service.delete_center(center_id)
        if center:
            return jsonify(center)
        return jsonify({"error": "Center not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@centers_bp.route('/centers/search', methods=['GET'])
def search_centers():
    """
    Search centers by name
    ---
    tags:
      - Centers
    parameters:
      - name: name
        in: query
        type: string
        required: true
    responses:
      200:
        description: List of centers matching the search criteria
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              center_name:
                type: string
              status:
                type: integer
      400:
        description: No search criteria provided
      500:
        description: Internal server error
    """
    try:
        name = request.args.get('name')
        if not name:
            return jsonify({"error": "Please provide name for search"}), 400

        centers = service.search_centers_by_name(name)
        return jsonify(centers)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
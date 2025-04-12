from flask import Blueprint, request, jsonify
from services.image_processor import ImageProcessor
from services.academic.exam_distribution_service import ExamDistributionService
from database.vectors_repository import VectorsRepository
from services.vectors_service import VectorsService
from werkzeug.utils import secure_filename
import os
import json

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")

exam_distribution = ExamDistributionService()
repository = VectorsRepository()
vectors = VectorsService(repository)

identity_routes = Blueprint("identity_routes", __name__)

@identity_routes.route("/identity/verify", methods=["POST"])
def verify_student_and_device():
    """
    Verify student identity, device, and perform facial recognition
    ---
    tags:
      - Identity Verification
    consumes:
      - multipart/form-data
    parameters:
      - name: image
        in: formData
        type: file
        required: true
        description: Image file (face).
      - name: student_id
        in: formData
        type: string
        required: true
        description: The student's registration number.
      - name: device_id
        in: formData
        type: integer
        required: true
        description: The device ID.
    responses:
      200:
        description: Verification results
        schema:
          type: object
          properties:
            student_data:
              type: object
              description: Complete student data
            device_check:
              type: object
              properties:
                is_correct:
                  type: boolean
                correct_device_id:
                  type: integer
            face_check:
              type: object
              properties:
                is_match:
                  type: boolean
                confidence:
                  type: number
      400:
        description: Invalid input data
      404:
        description: Student not found or no stored vector
      422:
        description: Face processing error
      500:
        description: Server error
    """
    try:
        # 1. Basic input validation
        if "image" not in request.files:
            return jsonify({"error": "Image file is required"}), 400

        image_file = request.files["image"]
        student_id = request.form.get("student_id")
        device_id = request.form.get("device_id", type=int)

        if not student_id:
            return jsonify({"error": "Student ID is required"}), 400
        if not device_id:
            return jsonify({"error": "Device ID is required"}), 400

        # 2. Get student data
        try:
            student_data = exam_distribution.get_student_info(student_id)
        except ValueError as e:
            return jsonify({"error": str(e)}), 404

        # 3. Verify device
        correct_device_id = student_data.get("device_number")
        device_verified = correct_device_id == device_id

        # 4. Face verification
        face_verified = False
        confidence = 0.0
        temp_file_path = None

        try:
            # Save temporary image
            temp_file_path = os.path.join(UPLOAD_FOLDER, secure_filename(image_file.filename))
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            image_file.save(temp_file_path)

            # Get stored vector - returns error if not found
       
            stored_vector = vectors.get_vector_by_id(student_id)

            v=json.loads(stored_vector['vector'])

            if not v:
                return jsonify({"error": "No face vector found for student"}), 404
               
            # Convert current image to vector - returns error if fails
            current_vector = ImageProcessor.convert_image_to_vector(temp_file_path)

            # Compare vectors - only returns False if vectors don't match
            face_verified, confidence = ImageProcessor.compare_vectors(v, current_vector)

        except Exception as e:
            if "convert_image_to_vector" in str(e):
                return jsonify({"error": f"Image processing failed: {str(e)}"}), 422
            return jsonify({"error": str(e)}), 500
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)

        # 5. Prepare final response
        response = {
            "student_data": student_data,
            "device_check": {
                "is_correct": device_verified,
                "correct_device_id": correct_device_id
            },
            "face_check": {
                "is_match": face_verified,
                "confidence":round(confidence, 4)
            }
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


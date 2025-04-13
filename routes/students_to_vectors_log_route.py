#هذه املف لتصدير ملف log التي تسجل بها الاخطاء ويتم ارسالها عبر api 
from flasgger import Swagger
from flask import Blueprint, jsonify, Response
import os

log_bp = Blueprint('logs', __name__)

LOG_FILE_PATH = os.path.join("logs", "students_to_vectors.log")

@log_bp.route('/logs/students', methods=['GET'])
def get_student_logs():
    """
    Get student vector log file contents
    ---
    summary: Get students log file
    tags:
      - Logs
    responses:
      200:
        description: Log content returned successfully
        content:
          text/plain:
            schema:
              type: string
              example: "2025-04-13 10:00:00 - ERROR - Student ID not found\n..."
      404:
        description: Log file not found
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
      500:
        description: Internal server error
    """
    try:
        if not os.path.exists(LOG_FILE_PATH):
            return jsonify({'error': 'Log file not found'}), 404

        with open(LOG_FILE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()

        return Response(content, mimetype='text/plain')
    except Exception as e:
        return jsonify({'error': f'Failed to read log file: {str(e)}'}), 500
    



@log_bp.route('/logs/students/clear', methods=['POST'])
def clear_student_logs():
    """
    Clear student vector log file contents
    ---
    summary: Clear students log file
    tags:
      - Logs
    responses:
      200:
        description: Log file cleared successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Log file cleared successfully
      500:
        description: Failed to clear log file
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
    """
    try:
        open(LOG_FILE_PATH, 'w', encoding='utf-8').close()
        return jsonify({'message': 'Log file cleared successfully'})
    except Exception as e:
        return jsonify({'error': f'Failed to clear log file: {str(e)}'}), 500

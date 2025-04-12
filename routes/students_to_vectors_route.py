from flask import Blueprint, request, jsonify
from services.students_to_vectors_service import StudentsToVectorsService

students_to_vectors_route = Blueprint('students_to_vectors_route', __name__)

@students_to_vectors_route.route('/api/students-to-vectors', methods=['POST', 'OPTIONS'])
def students_to_vectors():
    """
    Process students to vectors using Student IDs
    ---
    tags:
      - Convert S to V
    parameters:
        - name: student_ids
          in: body
          required: true
          schema:
            type: array
            items:
              type: integer
            example: [1, 2, 3]
    responses:
      200:
        description: Success response
        schema:
          type: object
          properties:
            message:
              type: string
            success_count:
              type: integer
            failure_count:
              type: integer
            failure_details:
              type: array
              items:
                type: object
                properties:
                  student_id:
                    type: integer
                  error:
                    type: string
      400:
        description: Invalid input
        schema:
          type: object
          properties:
            error:
              type: string
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
    """
    if request.method == 'OPTIONS':
        # الرد على طلب OPTIONS
        response = jsonify({"message": "Preflight request accepted"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "POST")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        return response

    try:
        # استقبال معرفات الطلاب من الطلب
        student_ids = request.json
        # print("dsf")
        # print(student_ids)

        # التحقق من صحة المدخلات
        if not student_ids or not isinstance(student_ids, list):
          #print(student_ids)
          return jsonify({"error": "Input must be a non-empty list of Student IDs"}), 400

        # معالجة الطلاب وتحويل الصور إلى فكتورز
        result = StudentsToVectorsService.process_students_to_vectors(student_ids)

        # إرجاع النتيجة
        return jsonify(result), 200
    except ValueError as e:
        # معالجة الأخطاء المتوقعة (مثل مدخلات غير صالحة)
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # معالجة الأخطاء غير المتوقعة
        return jsonify({"error": "An unexpected error occurred."}), 500
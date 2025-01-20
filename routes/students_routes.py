from flask import Blueprint, jsonify, request
from services.students_service import(
  get_all_students, add_student,
  search_students_by_name,
  search_student_by_number,
  fetch_student_info_by_number,
  fetch_students_by_ids
)
from flasgger import Swagger, swag_from


# إنشاء Blueprint للمسارات

students_bp = Blueprint('students_bp', __name__, url_prefix='/students')

@students_bp.route('/add', methods=['POST'])
@swag_from({
    'tags': ['Students'],
    'parameters': [
        {
            "name": "StudentName",
            "in": "formData",
            "type": "string",
            "required": True,
            "description": "Student's name"
        },
        {
            "name": "Number",
            "in": "formData",
            "type": "string",
            "required": True,
            "description": "Enrollment number"
        },
        {
            "name": "College",
            "in": "formData",
            "type": "string",
            "required": True,
            "description": "College name"
        },
        {
            "name": "Level",
            "in": "formData",
            "type": "string",
            "required": True,
            "description": "Student level (1 character)"
        },
        {
            "name": "Specialization",
            "in": "formData",
            "type": "string",
            "required": True,
            "description": "Specialization"
        },
        {
            "name": "Gender",
            "in": "formData",
            "type": "integer",
            "required": True,
            "description": "Gender (0 for female, 1 for male)"
        },
        {
            "name": "image",
            "in": "formData",
            "type": "file",
            "required": True,
            "description": "Student's image file (PNG, JPG, JPEG)"
        }
    ],
    'responses': {
        201: {
            "description": "Student added successfully"
        },
        400: {
            "description": "Bad Request (e.g., duplicate enrollment number or invalid image)"
        },
        500: {
            "description": "Internal Server Error"
        }
    }
})
def add_student_route():
    data = {
        "StudentName": request.form.get('StudentName'),
        "Number": request.form.get('Number'),
        "College": request.form.get('College'),
        "Level": request.form.get('Level'),
        "Specialization": request.form.get('Specialization'),
        "Gender": int(request.form.get('Gender')),
    }
    image_file = request.files.get('image')

    result, status_code = add_student(data, image_file)
    return jsonify(result), status_code



@students_bp.route('/', methods=['GET'])
def get_students():
    """
    Get all students
    ---
    tags:
      - Students
    responses:
      200:
        description: A list of all students
    """
    students = get_all_students()
    return jsonify(students)



@students_bp.route('/search', methods=['GET'])
def search_student():
    """
    Search for a student by enrollment number or name
    ---
    tags:
      - Students
    parameters:
      - name: number
        in: query
        type: string
        required: false
        description: The enrollment number of the student
      - name: name
        in: query
        type: string
        required: false
        description: The name (or part of it) of the student
    responses:
      200:
        description: List of students or a single student
      400:
        description: Invalid request (no search parameters provided)
      404:
        description: No students found
    """
    number = request.args.get('number')
    name = request.args.get('name')

    if number:
        # البحث برقم القيد
        student = search_student_by_number(number)
        if student:
            return jsonify([student])  # إرجاع نتيجة كمصفوفة لتوحيد الردود
        return jsonify({"error": "No student found with the provided enrollment number"}), 404

    elif name:
        # البحث بالاسم
        students = search_students_by_name(name)
        if students:
            return jsonify(students)
        return jsonify({"error": "No students found with the provided name"}), 404

    # إذا لم يتم توفير أي استعلام
    return jsonify({"error": "Please provide either 'number' or 'name' as a search parameter"}), 400



@students_bp.route('/info', methods=['GET'])
def get_student_info():
    """
    Get the enrollment number, college, and image path of a student by their enrollment number
    ---
    tags:
      - Students
    parameters:
      - name: number
        in: query
        type: string
        required: true
        description: The enrollment number of the student
    responses:
      200:
        description: Student info retrieved successfully
        schema:
          type: object
          properties:
            Number:
              type: string
              description: The enrollment number of the student
            College:
              type: string
              description: The college of the student
            ImagePath:
              type: string
              description: The path to the student's image
      404:
        description: Student not found
    """
    number = request.args.get('number')
    if not number:
        return jsonify({"error": "Enrollment number is required"}), 400

    student_info = fetch_student_info_by_number(number)
    if student_info:
        return jsonify({
            "Number": student_info[0],
            "College": student_info[1],
            "ImagePath": student_info[2]
        })

    return jsonify({"error": "Student not found"}), 404


@students_bp.route('/by-ids', methods=['POST'])
def get_students_by_ids():
    """
    Retrieve students by their IDs
    ---
    tags:
      - Students
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            ids:
              type: array
              items:
                type: integer
              description: List of student IDs
    responses:
      200:
        description: A list of students matching the provided IDs
      400:
        description: Invalid request (no IDs provided)
      404:
        description: No students found with the provided IDs
    """
    data = request.get_json()
    ids = data.get('ids', [])
    
    if not ids:
        return jsonify({"error": "No IDs provided"}), 400

    students = fetch_students_by_ids(ids)
    if students:
        return jsonify(students)
    else:
        return jsonify({"error": "No students found with the provided IDs"}), 404
from database.exam_schedule import ExamSchedule

class ExamService:
    def __init__(self, db_name="database/students.db"):
        self.exam_schedule = ExamSchedule(db_name)

    def add_exam(self, student_number, subject, seat_number, exam_room, exam_center, exam_datetime, duration):
        self.exam_schedule.add_exam(student_number, subject, seat_number, exam_room, exam_center, exam_datetime, duration)

    def get_all_exams(self):
        return self.exam_schedule.get_all_exams()

    def find_exam_by_student_number(self, student_number):
        return self.exam_schedule.find_by_student_number(student_number)

    def update_exam(self, student_number, **kwargs):
        self.exam_schedule.update_exam(student_number, **kwargs)

    def delete_exam_by_student_number(self, student_number):
        self.exam_schedule.delete_exam_by_student_number(student_number)
    
    def delete_exam_by_id(self, exam_id):
        self.exam_schedule.delete_exam_by_id(exam_id)

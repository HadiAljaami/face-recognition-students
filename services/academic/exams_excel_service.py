# service.py
import pandas as pd
from io import BytesIO
from datetime import date, time
import os
import datetime
from database.academic.exam_excel_repository import ExamsExcelRepository

class ExamsExcelService:
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'.xlsx', '.xls'}
    
    REQUIRED_COLUMNS = [
        'course_id', 'major_id', 'college_id', 'level_id',
        'year_id', 'semester_id', 'exam_date', 'exam_start_time', 'exam_end_time'
    ]

    def __init__(self):
        self.repo = ExamsExcelRepository()

    def import_exams_from_excel(self, file_stream: BytesIO, filename: str) -> dict:
        self._validate_file(file_stream, filename)
       
        try:

            # التأكد من أن مؤشر القراءة في بداية الملف
            file_stream.seek(0)

            df = pd.read_excel(file_stream)
            if df.empty:
                raise ValueError("Uploaded file is empty")
            df.columns = [col.strip() for col in df.columns]
        
            self._validate_columns(df.columns)
           
            # إعادة تعيين المؤشر مرة أخرى بعد التحقق
            file_stream.seek(0)

            exams_data, validation_errors = self._prepare_exams_data(df)
           
            if validation_errors:
                return {
                    'status': 'validation_failed',
                    'total_records': len(df),
                    'invalid_records': validation_errors,
                    'message': 'Data validation failed'
                }
            
            db_validation_errors = self.repo.validate_exams_data(exams_data)
           
            if db_validation_errors:
                return self._format_db_validation_errors(db_validation_errors, df)
            
            self.repo.bulk_create_exams(exams_data)
          
            return {
                'status': 'success',
                'total_records': len(exams_data),
                'message': 'All exams imported successfully'
            }
            
        except Exception as e:
            raise RuntimeError(f"Import process failed: {str(e)}")

    def _validate_file(self, file_stream: BytesIO, filename: str):
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in self.ALLOWED_EXTENSIONS:
            raise ValueError(f"File must be Excel format ({', '.join(self.ALLOWED_EXTENSIONS)})")
        
        file_stream.seek(0, os.SEEK_END)
        file_size = file_stream.tell()
        file_stream.seek(0)
        
        if file_size > self.MAX_FILE_SIZE:
            raise ValueError(f"File size too large (max {self.MAX_FILE_SIZE//1024//1024}MB)")

    def _validate_columns(self, columns):
        cleaned_columns = [str(col).strip() for col in columns]
        missing = [col for col in self.REQUIRED_COLUMNS if col not in cleaned_columns]
        if missing:
            raise ValueError(f"Required columns missing: {', '.join(missing)}")

    def _prepare_exams_data(self, df: pd.DataFrame) -> tuple:
        exams_data = []
        validation_errors = []
        print('Preparing and validating exams data')
       
        for index, row in df.iterrows():
            try:
                record = (
                    self._convert_int(row['course_id']),
                    self._convert_int(row['major_id']),
                    self._convert_int(row['college_id']),
                    self._convert_int(row['level_id']),
                    self._convert_int(row['year_id']),
                    self._convert_int(row['semester_id']),
                    self._convert_date(row['exam_date']),
                    self._convert_time(row['exam_start_time']),
                    self._convert_time(row['exam_end_time'])
                )
                
                if record[-2] >= record[-1]:
                    raise ValueError("Start time must be before end time")
                    
                exams_data.append(record)
            except ValueError as e:
                validation_errors.append({
                    'row': index + 2,
                    'error': str(e),
                    'data': self._get_row_data(row)
                })
        return exams_data, validation_errors

    def _format_db_validation_errors(self, db_errors, df):
        errors = []
        for idx, error_msg in db_errors:
            row_data = df.iloc[idx]
            errors.append({
                'row': idx + 2,
                'error': self._translate_db_error(error_msg),
                'data': self._get_row_data(row_data)
            })
        
        return {
            'status': 'validation_failed',
            'total_records': len(df),
            'invalid_records': errors,
            'message': 'Database validation failed'
        }

    def _translate_db_error(self, error_msg: str) -> str:
        if "null value in column" in error_msg:
            return "Required value is missing"
        elif "invalid input syntax for type integer" in error_msg:
            return "Must be an integer value"
        elif "invalid input syntax for type date" in error_msg:
            return "Invalid date format (expected YYYY-MM-DD)"
        elif "invalid input syntax for type time" in error_msg:
            return "Invalid time format (expected HH:MM)"
        elif "violates foreign key constraint" in error_msg:
            return "Reference value does not exist"
        return error_msg

    def _convert_int(self, value) -> int:
        if pd.isna(value):
            raise ValueError("Required value is missing")
        try:
            return int(float(value))
        except (ValueError, TypeError):
            raise ValueError("Must be an integer value")

    def _convert_date(self, value) -> date:
        if pd.isna(value):
            raise ValueError("Exam date is required")
        try:
            if isinstance(value, str):
                return datetime.strptime(value, '%Y-%m-%d').date()
            elif isinstance(value, date):
                return value
            return pd.to_datetime(value).date()
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid date format: {value}")

    def _convert_time(self, value) -> time:
        if pd.isna(value):
            raise ValueError("Exam time is required")
        try:
            if isinstance(value, str):
                if ':' in value:
                    parts = value.split(':')
                    hours = int(parts[0])
                    minutes = int(parts[1])
                    
                    if not (0 <= hours < 24):
                        raise ValueError(f"Hours must be between 0-23 (got: {hours})")
                    if not (0 <= minutes < 60):
                        raise ValueError(f"Minutes must be between 0-59 (got: {minutes})")
                    
                    return time(hours, minutes)
            elif isinstance(value, time):
                return value
            return pd.to_datetime(value).time()
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid time format: {value}")
        
    def _get_row_data(self, row: pd.Series) -> dict:
        return {
            col: str(row[col]) if not pd.isna(row[col]) else 'NULL'
            for col in self.REQUIRED_COLUMNS
        }
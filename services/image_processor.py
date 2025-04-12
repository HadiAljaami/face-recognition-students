import os
import face_recognition
from werkzeug.utils import secure_filename
import numpy as np

class ImageProcessor:
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    MAX_FILE_SIZE_MB = 5
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    LAMBDA = 0.5  # Factor to balance size vs. position in face selection

    @staticmethod
    def allowed_file(filename):
        """Check if the file has an allowed extension."""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ImageProcessor.ALLOWED_EXTENSIONS
    
    @staticmethod
    def secure_filename(filename):
        """Secure the filename."""
        return secure_filename(filename)
    
    @staticmethod
    def check_image_size(image_path):
        """Check if the image size is within the allowed limit."""
        file_size = os.path.getsize(image_path)
        if file_size > ImageProcessor.MAX_FILE_SIZE_BYTES:
            raise ValueError(f"Image size exceeds the maximum allowed size of {ImageProcessor.MAX_FILE_SIZE_MB}MB.")
        return True

    @staticmethod
    def extract_best_face_vector(image):
        """Extract the best face vector from an image using a mix of size and position."""
        face_locations = face_recognition.face_locations(image)  # Using default model for better accuracy
        if not face_locations:
            raise ValueError("No face detected in the image.")
        
        if len(face_locations) == 1:
            # Directly process a single detected face without passing `known_face_locations`
            face_encodings = face_recognition.face_encodings(image)
            if not face_encodings:
                raise ValueError("Unable to extract face vector.")
            return face_encodings[0].tolist()
        
        # Multiple faces detected → Select the best face based on size and position
        image_height, image_width, _ = image.shape
        image_center_x, image_center_y = image_width // 2, image_height // 2
        
        def calculate_score(face):
            top, right, bottom, left = face
            width, height = right - left, bottom - top
            size = width * height
            face_center_x, face_center_y = left + width // 2, top + height // 2
            distance = ((face_center_x - image_center_x) ** 2 + (face_center_y - image_center_y) ** 2) ** 0.5
            return size - (ImageProcessor.LAMBDA * distance)
        
        best_face = max(face_locations, key=calculate_score)
        
        # Compute encoding only for the selected face
        face_encodings = face_recognition.face_encodings(image, known_face_locations=[best_face])
        if not face_encodings:
            raise ValueError("Unable to extract face vector.")
        
        return face_encodings[0].tolist()

    @staticmethod
    def convert_image_to_vector(image_path):
        """Convert an image to a face vector."""
        try:
            # Check file extension
            if not ImageProcessor.allowed_file(image_path):
                raise ValueError(f"File type not allowed. Allowed types: {ImageProcessor.ALLOWED_EXTENSIONS}")

            # Check image size
            ImageProcessor.check_image_size(image_path)

            # Load the image
            image = face_recognition.load_image_file(image_path)

            # Extract the best face vector
            return ImageProcessor.extract_best_face_vector(image)
        except Exception as e:
            raise ValueError(f"Error processing image: {str(e)}")
    
    @staticmethod
    def compare_vectors(vector1, vector2, tolerance=0.6):
        """
        Compare two face vectors and return similarity score
        """
        try:
            vector1 = np.array(vector1, dtype=np.float32)
            vector2 = np.array(vector2, dtype=np.float32)

            # التحقق من أن المتجهات غير فارغة
            if vector1.size == 0 or vector2.size == 0:
                raise ValueError("Empty vectors provided")

            # التحقق من أن الأبعاد متساوية
            if vector1.shape != vector2.shape:
                raise ValueError("Vectors have different dimensions")

            # التحقق من أن القيم كلها أرقام
            if not all(isinstance(x, (int, float)) for x in vector1.tolist() + vector2.tolist()):
                raise ValueError("Vectors contain non-numeric values")

            # حساب المسافة
            distance = face_recognition.face_distance([vector1], vector2)[0]
            confidence_score = 1 - distance
            match_result = distance <= tolerance

            return bool(match_result), float(confidence_score)

        except Exception as e:
            raise ValueError(f"Vector comparison failed: {str(e)}")
            
    # @staticmethod
    # def compare_vectors(vector1, vector2, tolerance=0.6):
    #     """
    #     Compare two face vectors and return similarity score
        
    #     Args:
    #         vector1: First face vector (list of floats)
    #         vector2: Second face vector (list of floats)
    #         tolerance: Threshold for face matching (default 0.6)
            
    #     Returns:
    #         Tuple of (match_result: bool, confidence_score: float)
            
    #     Raises:
    #         ValueError: If vectors are invalid or incompatible
    #     """

    #     try:
    #         vector1 = np.array(vector1, dtype=np.float32)
    #         vector2 = np.array(vector2, dtype=np.float32)
    #         # التحقق من أن المتجهات صالحة
    #         # if not vector1 or not vector2:
    #         #     raise ValueError("Empty vectors provided")
    #         if vector1.size == 0 or vector2.size == 0:
    #             raise ValueError("Empty vectors provided")
    
    #         if len(vector1) != len(vector2):
    #             raise ValueError("Vectors have different dimensions")
           
           
    #         if not all(isinstance(x, (int, float)) for x in np.concatenate((vector1, vector2))):
    #             raise ValueError("Vectors contain non-numeric values")



    #         # if not all(isinstance(x, (int, float)) for x in vector1 + vector2):
    #         #     raise ValueError("Vectors contain non-numeric values")
            


            
    #         print("v1 type:", type(vector1), "sample:", vector1[:5])
    #         print("v2 type:", type(vector2), "sample:", vector2[:5])

    #         # حساب المسافة بين المتجهات
    #         distance = face_recognition.face_distance([vector1], vector2)[0]
            
    #         # تحويل المسافة إلى درجة تشابه (0-1)
    #         confidence_score = 1 - distance
            
    #         # تحديد إذا كانت تطابق بناء على tolerance
    #         match_result = distance <= tolerance
            
    #         return match_result, confidence_score
            
    #     except Exception as e:
    #         raise ValueError(f"Vector comparison failed: {str(e)}")

    # @staticmethod
    # def compare_vectors(vector1, vector2, tolerance=0.6):
    #     """
    #     Compare vectors with automatic format handling
    #     """
    #     try:
    #         import numpy as np
            
    #         # تحويل المتجهات إلى numpy arrays
    #         def to_array(v):
    #             if isinstance(v, str):
    #                 # معالجة السلسلة النصية
    #                 if v.startswith('[') and v.endswith(']'):
    #                     return np.fromstring(v[1:-1], sep=',', dtype=float)
    #                 return np.frombuffer(v.encode(), dtype=float)
    #             return np.array(v, dtype=float)
            
    #         v1 = to_array(vector1)
    #         v2 = to_array(vector2)
            
    #         # التحقق من الأبعاد
    #         if v1.shape != v2.shape:
    #             raise ValueError(f"Shape mismatch: {v1.shape} vs {v2.shape}")
                
    #         # المقارنة
    #         distance = face_recognition.face_distance([v1], v2)[0]
    #         return (distance <= tolerance), float(1 - distance)
            
    #     except Exception as e:
    #         raise ValueError(f"Comparison failed: {str(e)}")
        
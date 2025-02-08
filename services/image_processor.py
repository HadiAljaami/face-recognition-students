import os
import face_recognition
from werkzeug.utils import secure_filename

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

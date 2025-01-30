import os
import face_recognition
from werkzeug.utils import secure_filename

class ImageProcessor:
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    MAX_FILE_SIZE_MB = 5
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

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
    def validate_image(image):
        """Validate the image by ensuring it contains exactly one face."""
        face_locations = face_recognition.face_locations(image)
        if len(face_locations) != 1:
            raise ValueError("Image must contain exactly one face.")
        return True

    @staticmethod
    def extract_face_vector(image):
        """Extract the face vector from an image."""
        face_encodings = face_recognition.face_encodings(image)
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

            # Load the image once
            image = face_recognition.load_image_file(image_path)

            # Validate the image (check for exactly one face)
            ImageProcessor.validate_image(image)

            # Extract the face vector
            vector = ImageProcessor.extract_face_vector(image)
            return vector
        except Exception as e:
            # Raise the exception to be handled by the caller
            raise
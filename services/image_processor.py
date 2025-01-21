import os
import cv2
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
        if len(face_locations) < 1:
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

            image = cv2.resize(image, (0, 0), fx=0.5, fy=0.5)
            print("Load the image once")
            # Choose the best face
            face_locations = face_recognition.face_locations(image)
            
            if not face_locations:
                raise ValueError("No faces were discovered in the picture")
            
            # Extract the encoding for the selected face
            face_encodings = face_recognition.face_encodings(image, known_face_locations=[face_locations[0]])
            print("face_encodings")
            if not face_encodings:
                raise ValueError("Unable to extract face vector.")

            # # Validate the image (check for exactly one face)
            # ImageProcessor.validate_image(image)

            # # Extract the face vector
            # vector = ImageProcessor.extract_face_vector(image)

            return face_encodings[0].tolist()
        except Exception as e:
            # Raise the exception to be handled by the caller
            raise

    @staticmethod
    def select_best_face(image, face_locations):
        """ Select the best face based on clarity and centrality."""
        best_face_index = 0
        max_score = -float('inf')
        img_height, img_width = image.shape[:2]
        center = (img_width // 2, img_height // 2)
        for i, (top, right, bottom, left) in enumerate(face_locations):
            # Calculate diversity (example using variance)
            face_image = image[top:bottom, left:right]
            clarity = face_image.var() # Measuring contrast as an alternative to clarity

            # Calculate the distance from the center
            face_center = ((left + right) // 2, (top + bottom) // 2)
            distance = ((face_center[0] - center[0])**2 + (face_center[1] - center[1])**2)**0.5

            # Calculating points (the smaller the distance and the greater the clarity, the higher the points)
            score = clarity * 0.7 + (1 / (distance +1)) * 0.3  # Modifiable weights

            if score > max_score:
                max_score = score
                best_face_index = i
        return best_face_index


    #
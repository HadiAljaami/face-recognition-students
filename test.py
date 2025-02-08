import face_recognition
import cv2
import numpy as np
from matplotlib import pyplot as plt

def plot_images(images, titles):
    """Helper function to display images side by side."""
    plt.figure(figsize=(15, 5))
    for i, (image, title) in enumerate(zip(images, titles)):
        plt.subplot(1, len(images), i + 1)
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        plt.title(title)
        plt.axis('off')
    plt.show()

# 1. تحميل الصورة
image_path = "path_to_your_image.jpg"  # ضع مسار الصورة هنا
image = cv2.imread(image_path)

# عرض الصورة الأصلية
plot_images([image], ["Original Image"])

# 2. كشف الوجه باستخدام face_locations
face_locations = face_recognition.face_locations(image)

# رسم المستطيلات حول الوجوه المكتشفة
image_with_faces = image.copy()
for (top, right, bottom, left) in face_locations:
    cv2.rectangle(image_with_faces, (left, top), (right, bottom), (0, 255, 0), 2)

# عرض الصورة بعد الكشف عن الوجه
plot_images([image_with_faces], ["Face Detection"])

# 3. استخراج المتجهات باستخدام face_encodings
face_encodings = face_recognition.face_encodings(image, face_locations)

# طباعة المتجهات
if face_encodings:
    print("Face Encodings Vector (First Face):")
    print(face_encodings[0])  # طباعة أول متجه
else:
    print("No face encodings found.")

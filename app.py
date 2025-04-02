from flask import Flask, redirect, url_for
from flasgger import Swagger
from flask_cors import CORS
#from flask_jwt_extended import JWTManager # dont delete !!!

from routes.students_routes import students_bp
from routes.vectors_routes import vectors_routes  # استيراد المسارات الجديدة
from routes.students_to_vectors_route import students_to_vectors_route
from routes.centers_routes import centers_bp
from routes.users_routes import users_bp
from routes.devices_routes import devices_bp

from routes.exam_distribution_routes import exam_routes

#------------academic------------------
from routes.academic.colleges_routes import colleges_bp
# -----------------------------

app = Flask(__name__)

# إعداد Swagger
swagger = Swagger(app)
app.static_url_path = "/static"
app.static_folder = "database/student_images"

CORS(app)

# تسجيل المسارات
app.register_blueprint(students_bp)
app.register_blueprint(vectors_routes, url_prefix="/vectors")  # تحديد المسار الأساسي لمسارات المتجهات
app.register_blueprint(students_to_vectors_route)
#app.register_blueprint(centers_bp, url_prefix='/api')
app.register_blueprint(users_bp)
app.register_blueprint(centers_bp)
#app.register_blueprint(devices_bp)

app.register_blueprint(exam_routes)#, url_prefix="/exams"

#------------academic------------------
app.register_blueprint(colleges_bp)
# -----------------------------

#----------don't delete----------------------
# # JWT Configuration
# app.config["JWT_SECRET_KEY"] = "super-secret-key"  # تغيير هذا المفتاح في البيئة الإنتاجية
# jwt = JWTManager(app)
#-------------------------------------------

# إضافة مسار الصفحة الرئيسية
@app.route('/')
def home():
    # توجيه المستخدم تلقائيًا إلى صفحة التوثيق
    return redirect(url_for('flasgger.apidocs'))

if __name__ == '__main__':
    app.run(debug=True)

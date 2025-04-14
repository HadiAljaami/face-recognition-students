from flask import Flask, redirect, url_for, jsonify
from flasgger import Swagger
from flask_cors import CORS
from flask_jwt_extended import JWTManager # dont delete !!!
from datetime import timedelta
# import secrets
# print(secrets.token_hex(32)) # this is to create  JWT_SECRET_KEY in line # 70

from routes.students_routes import students_bp
from routes.vectors_routes import vectors_routes  # استيراد المسارات الجديدة
from routes.students_to_vectors_route import students_to_vectors_route
from routes.students_to_vectors_log_route import log_bp

from routes.centers_routes import centers_bp
from routes.users_routes import users_bp
from routes.devices_routes import devices_bp

from routes.exam_distribution_routes import exam_routes

#------------academic------------------
from routes.academic.exams_routes import init_app
from routes.academic.colleges_routes import colleges_bp
from routes.academic.majors_routes import majors_bp
from routes.academic.levels_routes import levels_bp
from routes.academic.academic_years_routes import years_bp
from routes.academic.semesters_routes import semesters_bp
from routes.academic.courses_routes import courses_bp
from routes.academic.exams_routes import exams_bp
from routes.academic.exam_distribution_router import exam_distribution_bp
# -----------monitoring----------------------
from routes.monitoring.alert_type_routes import alert_type_bp
from routes.monitoring.alert_routes import alert_bp
from routes.monitoring.check_image_seat_student import identity_routes
from routes.monitoring.model_config_routes import model_config_bp
#-----------------------------------------------

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
app.register_blueprint(log_bp)
#app.register_blueprint(centers_bp, url_prefix='/api')
app.register_blueprint(users_bp)
app.register_blueprint(centers_bp)
app.register_blueprint(devices_bp)

app.register_blueprint(exam_routes)#, url_prefix="/exams"

#------------academic------------------

app.register_blueprint(colleges_bp)
app.register_blueprint(majors_bp)
app.register_blueprint(levels_bp)
app.register_blueprint(years_bp)
app.register_blueprint(semesters_bp)
app.register_blueprint(courses_bp)
app.register_blueprint(exams_bp)
app.register_blueprint(exam_distribution_bp)
init_app(app)# for all time and date 
#-----------------monitoring--------------------------

app.register_blueprint(alert_type_bp)
app.register_blueprint(alert_bp)
app.register_blueprint(identity_routes)
app.register_blueprint(model_config_bp )
#------------------------------------------
#----------don't delete----------------------
# # JWT Configuration
app.config["JWT_SECRET_KEY"] = "9a41d4bba2dc946aef73bb59669e0bc53527c3eb107af5efaafbd77c5619da11"  # تغيير هذا المفتاح في البيئة الإنتاجية
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
jwt = JWTManager(app)
#-------------------------------------------

# إضافة مسار الصفحة الرئيسية
@app.route('/')
def home():
    # توجيه المستخدم تلقائيًا إلى صفحة التوثيق
    return redirect(url_for('flasgger.apidocs'))
    
@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'pong'}), 200

if __name__ == '__main__':
    app.run(debug=True)

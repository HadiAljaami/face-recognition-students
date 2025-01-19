from flask import Flask, redirect, url_for
from flasgger import Swagger
from routes.students_routes import students_bp
from flask_cors import CORS


from routes.vectors_routes import vectors_routes  # استيراد المسارات الجديدة
from routes.students_to_vectors_route import students_to_vectors_route
app = Flask(__name__)

# إعداد Swagger
swagger = Swagger(app)
app.static_url_path = "/static"
app.static_folder = "database/student_images"
CORS(app, origins=["http://localhost:3000"]) 
CORS(app, origins=["http://localhost:5173"]) 

# تسجيل المسارات
app.register_blueprint(students_bp)
app.register_blueprint(vectors_routes, url_prefix="/vectors")  # تحديد المسار الأساسي لمسارات المتجهات
app.register_blueprint(students_to_vectors_route)

# إضافة مسار الصفحة الرئيسية
@app.route('/')
def home():
    # توجيه المستخدم تلقائيًا إلى صفحة التوثيق
    return redirect(url_for('flasgger.apidocs'))

if __name__ == '__main__':
    app.run(debug=True)

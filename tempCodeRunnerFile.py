

# إعداد Swagger
swagger = Swagger(app)
app.static_url_path = "/static"
app.static_folder = "database/student_images"

CORS(app)

# تسجيل المسارات
app.register_blueprint(students_bp)
app.register_blueprint(vectors_routes, url_prefix="/vectors")  # تحديد المسار الأساسي لمسارات المتجهات
app.register_bluepri
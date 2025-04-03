swagger = Swagger(app)
app.static_url_path = "/static"
app.static_folder = "database/student_images"

CORS(app)
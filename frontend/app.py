from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import requests
from functools import wraps

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")

API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://localhost:8000")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "token" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    """Homepage with course catalog"""
    try:
        courses_response = requests.get(f"{API_GATEWAY_URL}/api/v1/courses/courses/")
        courses = courses_response.json() if courses_response.ok else []
        return render_template("index.html", title="Plataforma de Cursos Online", courses=courses)
    except requests.RequestException as e:
        flash(f"Error al cargar los cursos: {str(e)}", "error")
        return render_template("index.html", title="Plataforma de Cursos Online", courses=[])

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            response = requests.post(
                f"{API_GATEWAY_URL}/api/v1/auth/token",
                data={
                    "username": request.form["email"],
                    "password": request.form["password"]
                }
            )
            if response.ok:
                data = response.json()
                session["token"] = data["access_token"]
                return redirect(url_for("dashboard"))
            flash("Credenciales inválidas", "error")
        except requests.RequestException:
            flash("Error al conectar con el servidor", "error")
    return render_template("login.html", title="Iniciar Sesión")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            response = requests.post(
                f"{API_GATEWAY_URL}/api/v1/auth/users/",
                json={
                    "email": request.form["email"],
                    "password": request.form["password"],
                    "full_name": request.form["full_name"],
                    "user_type": request.form["user_type"]
                }
            )
            if response.ok:
                flash("Registro exitoso. Por favor inicia sesión.", "success")
                return redirect(url_for("login"))
            flash("Error en el registro", "error")
        except requests.RequestException:
            flash("Error al conectar con el servidor", "error")
    return render_template("register.html", title="Registro")

@app.route("/dashboard")
@login_required
def dashboard():
    """Student dashboard with enrolled courses and progress"""
    try:
        headers = {"Authorization": f"Bearer {session['token']}"}
        
        # Get user info
        user_response = requests.get(
            f"{API_GATEWAY_URL}/api/v1/auth/users/me/",
            headers=headers
        )
        user = user_response.json()
        
        # Get student's progress
        progress_response = requests.get(
            f"{API_GATEWAY_URL}/api/v1/progress/student/{user['id']}/courses/",
            headers=headers
        )
        progress = progress_response.json() if progress_response.ok else []
        
        return render_template(
            "dashboard.html",
            title="Mi Dashboard",
            user=user,
            progress=progress
        )
    except requests.RequestException:
        flash("Error al cargar el dashboard", "error")
        return redirect(url_for("index"))

@app.route("/courses/<int:course_id>")
@login_required
def course_detail(course_id):
    """Course detail page with modules and lessons"""
    try:
        headers = {"Authorization": f"Bearer {session['token']}"}
        
        # Get course details
        course_response = requests.get(
            f"{API_GATEWAY_URL}/api/v1/courses/courses/{course_id}",
            headers=headers
        )
        course = course_response.json()
        
        # Get modules with lessons
        modules_response = requests.get(
            f"{API_GATEWAY_URL}/api/v1/courses/courses/{course_id}/modules/",
            headers=headers
        )
        modules = modules_response.json() if modules_response.ok else []
        
        return render_template(
            "course_detail.html",
            title=course["title"],
            course=course,
            modules=modules
        )
    except requests.RequestException:
        flash("Error al cargar el curso", "error")
        return redirect(url_for("index"))

@app.route("/lessons/<int:lesson_id>/quiz")
@login_required
def take_quiz(lesson_id):
    """Take a quiz for a lesson"""
    try:
        headers = {"Authorization": f"Bearer {session['token']}"}
        
        # Get quiz for lesson
        quiz_response = requests.get(
            f"{API_GATEWAY_URL}/api/v1/evaluations/lessons/{lesson_id}/quizzes/",
            headers=headers
        )
        quizzes = quiz_response.json()
        
        if not quizzes:
            flash("No hay evaluaciones disponibles para esta lección", "info")
            return redirect(url_for("dashboard"))
        
        quiz = quizzes[0]  # Get first quiz
        return render_template("quiz.html", title="Evaluación", quiz=quiz)
    except requests.RequestException:
        flash("Error al cargar la evaluación", "error")
        return redirect(url_for("dashboard"))

@app.route("/quiz/<int:quiz_id>/submit", methods=["POST"])
@login_required
def submit_quiz(quiz_id):
    """Submit a quiz attempt"""
    try:
        headers = {"Authorization": f"Bearer {session['token']}"}
        
        # Get user info
        user_response = requests.get(
            f"{API_GATEWAY_URL}/api/v1/auth/users/me/",
            headers=headers
        )
        user = user_response.json()
        
        # Submit answers
        answers = {}
        for key, value in request.form.items():
            if key.startswith("question_"):
                question_num = key.split("_")[1]
                answers[question_num] = int(value)
        
        submission_response = requests.post(
            f"{API_GATEWAY_URL}/api/v1/evaluations/quiz-attempts/",
            headers=headers,
            json={
                "quiz_id": quiz_id,
                "student_id": user["id"],
                "answers": answers
            }
        )
        
        if submission_response.ok:
            result = submission_response.json()
            flash(f"Calificación: {result['score']}%. {'Aprobado' if result['passed'] else 'No aprobado'}", "info")
        else:
            flash("Error al enviar la evaluación", "error")
            
        return redirect(url_for("dashboard"))
    except requests.RequestException:
        flash("Error al procesar la evaluación", "error")
        return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session.pop("token", None)
    return redirect(url_for("index"))


@app.route("/new")
def new_item():
    # Ruta mínima para que la plantilla use url_for('new_item') sin errores
    return redirect(url_for("index"))


@app.route("/health")
def health():
    return {"status": "ok", "service": "frontend"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

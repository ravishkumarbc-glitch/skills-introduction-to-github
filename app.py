import json
import os
import secrets
import uuid
import warnings
from datetime import datetime

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from werkzeug.utils import secure_filename

app = Flask(__name__)

_secret_key = os.environ.get("SECRET_KEY")
if not _secret_key:
    _secret_key = secrets.token_hex(32)
    warnings.warn(
        "SECRET_KEY environment variable is not set. A temporary key has been generated; "
        "sessions will not persist across restarts. Set SECRET_KEY before deploying.",
        stacklevel=1,
    )
app.secret_key = _secret_key

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
DATA_FILE = os.path.join(os.path.dirname(__file__), "courses.json")
ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "mp4", "mov", "avi", "png", "jpg", "jpeg", "gif", "txt", "md"}
MAX_CONTENT_MB = 100

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_MB * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------- data helpers ----------

def _load_courses():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_courses(courses):
    with open(DATA_FILE, "w", encoding="utf-8") as fh:
        json.dump(courses, fh, indent=2, ensure_ascii=False)


def _find_course(course_id):
    return next((c for c in _load_courses() if c["id"] == course_id), None)


def _allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------- routes ----------

@app.route("/")
def index():
    courses = _load_courses()
    return render_template("index.html", courses=courses)


@app.route("/courses/new", methods=["GET", "POST"])
def new_course():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()

        if not title:
            flash("Course title is required.", "danger")
            return render_template("course_form.html", course=None)

        courses = _load_courses()
        course = {
            "id": str(uuid.uuid4()),
            "title": title,
            "description": description,
            "category": category,
            "created_at": datetime.utcnow().isoformat(),
            "files": [],
        }
        courses.append(course)
        _save_courses(courses)
        flash("Course created successfully.", "success")
        return redirect(url_for("course_detail", course_id=course["id"]))

    return render_template("course_form.html", course=None)


@app.route("/courses/<course_id>")
def course_detail(course_id):
    course = _find_course(course_id)
    if course is None:
        abort(404)
    return render_template("course_detail.html", course=course)


@app.route("/courses/<course_id>/edit", methods=["GET", "POST"])
def edit_course(course_id):
    courses = _load_courses()
    course = next((c for c in courses if c["id"] == course_id), None)
    if course is None:
        abort(404)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()

        if not title:
            flash("Course title is required.", "danger")
            return render_template("course_form.html", course=course)

        course["title"] = title
        course["description"] = description
        course["category"] = category
        _save_courses(courses)
        flash("Course updated successfully.", "success")
        return redirect(url_for("course_detail", course_id=course_id))

    return render_template("course_form.html", course=course)


@app.route("/courses/<course_id>/delete", methods=["POST"])
def delete_course(course_id):
    courses = _load_courses()
    course = next((c for c in courses if c["id"] == course_id), None)
    if course is None:
        abort(404)

    # remove associated uploaded files
    for f in course.get("files", []):
        filepath = os.path.join(UPLOAD_FOLDER, f["stored_name"])
        if os.path.exists(filepath):
            os.remove(filepath)

    courses = [c for c in courses if c["id"] != course_id]
    _save_courses(courses)
    flash("Course deleted.", "success")
    return redirect(url_for("index"))


@app.route("/courses/<course_id>/upload", methods=["POST"])
def upload_file(course_id):
    courses = _load_courses()
    course = next((c for c in courses if c["id"] == course_id), None)
    if course is None:
        abort(404)

    if "file" not in request.files:
        flash("No file selected.", "danger")
        return redirect(url_for("course_detail", course_id=course_id))

    file = request.files["file"]
    if file.filename == "":
        flash("No file selected.", "danger")
        return redirect(url_for("course_detail", course_id=course_id))

    if not _allowed_file(file.filename):
        flash(f"File type not allowed. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}", "danger")
        return redirect(url_for("course_detail", course_id=course_id))

    original_name = secure_filename(file.filename)
    ext = original_name.rsplit(".", 1)[1].lower()
    stored_name = f"{uuid.uuid4().hex}.{ext}"
    file.save(os.path.join(UPLOAD_FOLDER, stored_name))

    course["files"].append({
        "id": str(uuid.uuid4()),
        "original_name": original_name,
        "stored_name": stored_name,
        "uploaded_at": datetime.utcnow().isoformat(),
        "size": os.path.getsize(os.path.join(UPLOAD_FOLDER, stored_name)),
    })
    _save_courses(courses)
    flash(f"'{original_name}' uploaded successfully.", "success")
    return redirect(url_for("course_detail", course_id=course_id))


@app.route("/courses/<course_id>/files/<file_id>/delete", methods=["POST"])
def delete_file(course_id, file_id):
    courses = _load_courses()
    course = next((c for c in courses if c["id"] == course_id), None)
    if course is None:
        abort(404)

    file_entry = next((f for f in course["files"] if f["id"] == file_id), None)
    if file_entry is None:
        abort(404)

    filepath = os.path.join(UPLOAD_FOLDER, file_entry["stored_name"])
    if os.path.exists(filepath):
        os.remove(filepath)

    course["files"] = [f for f in course["files"] if f["id"] != file_id]
    _save_courses(courses)
    flash(f"'{file_entry['original_name']}' deleted.", "success")
    return redirect(url_for("course_detail", course_id=course_id))


@app.route("/uploads/<filename>")
def serve_upload(filename):
    # NOTE: This endpoint serves files without authentication. In a multi-user
    # or production deployment, restrict access to authorised users only.
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == "__main__":
    # Use a production WSGI server (e.g. Gunicorn) instead of this development
    # server for any deployment beyond local testing.
    app.run(debug=False)

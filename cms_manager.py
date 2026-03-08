#!/usr/bin/env python3
"""
EduCMS Manager — Python CLI for managing all website content.

Usage:
    python3 cms_manager.py serve [--port PORT]
    python3 cms_manager.py courses  list|add|edit|delete
    python3 cms_manager.py students list|add|delete
    python3 cms_manager.py announcements list|add|edit|delete
    python3 cms_manager.py enrollments  list|add|delete
    python3 cms_manager.py grades       list|set|delete
    python3 cms_manager.py export
    python3 cms_manager.py reset
"""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "cms_data.json"
APP_JS = BASE_DIR / "js" / "app.js"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _gen_id() -> str:
    return str(uuid.uuid4())


def _load() -> dict:
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        sys.exit(f"[error] Data file not found: {DATA_FILE}\nRun 'python3 cms_manager.py reset' to create it.")
    except json.JSONDecodeError as exc:
        sys.exit(f"[error] Data file is not valid JSON: {exc}")


def _save(data: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"[saved] {DATA_FILE}")


def _prompt(label: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"  {label}{suffix}: ").strip()
    return value if value else default


def _choose(items: list, label: str = "item") -> dict | None:
    if not items:
        print(f"  No {label}s found.")
        return None
    for i, item in enumerate(items):
        desc = item.get("title") or item.get("name") or item.get("id")
        print(f"  {i + 1}. {desc}  (id={item['id']})")
    raw = input(f"  Choose {label} #: ").strip()
    try:
        idx = int(raw) - 1
        if 0 <= idx < len(items):
            return items[idx]
    except ValueError:
        pass
    print("  Invalid selection.")
    return None


def _col(text: str, code: str) -> str:
    """Wrap text in ANSI colour if the terminal supports it."""
    if sys.stdout.isatty():
        return f"\033[{code}m{text}\033[0m"
    return text


def _header(text: str) -> None:
    print(_col(f"\n{'─' * 56}", "90"))
    print(_col(f"  {text}", "1"))
    print(_col(f"{'─' * 56}", "90"))


# ---------------------------------------------------------------------------
# COURSES
# ---------------------------------------------------------------------------

def cmd_courses(args: argparse.Namespace) -> None:
    data = _load()
    courses = data["courses"]

    if args.action == "list":
        _header(f"Courses ({len(courses)} total)")
        for c in courses:
            status_col = "32" if c["status"] == "published" else "33"
            print(f"  {c['id']:6}  {_col(c['title'], '1'):45}  "
                  f"{_col(c['status'], status_col):10}  {c['category']}")

    elif args.action == "add":
        _header("Add Course")
        c = {
            "id": _gen_id(),
            "title":       _prompt("Title"),
            "category":    _prompt("Category", "General"),
            "description": _prompt("Description"),
            "instructor":  _prompt("Instructor", "Admin User"),
            "status":      _prompt("Status (published/draft)", "published"),
            "color":       _prompt("Hex color", "#1f6feb"),
            "createdAt":   _now(),
        }
        if not c["title"]:
            sys.exit("[error] Title is required.")
        courses.append(c)
        _save(data)
        print(f"[ok] Course '{c['title']}' added (id={c['id']}).")

    elif args.action == "edit":
        _header("Edit Course")
        c = _choose(courses, "course")
        if c is None:
            return
        print("  (Press Enter to keep current value)")
        c["title"]       = _prompt("Title",       c["title"])
        c["category"]    = _prompt("Category",    c["category"])
        c["description"] = _prompt("Description", c["description"])
        c["instructor"]  = _prompt("Instructor",  c["instructor"])
        c["status"]      = _prompt("Status",      c["status"])
        c["color"]       = _prompt("Hex color",   c["color"])
        _save(data)
        print(f"[ok] Course '{c['title']}' updated.")

    elif args.action == "delete":
        _header("Delete Course")
        c = _choose(courses, "course")
        if c is None:
            return
        confirm = input(f"  Delete '{c['title']}'? (y/N): ").strip().lower()
        if confirm == "y":
            data["courses"] = [x for x in courses if x["id"] != c["id"]]
            data["enrollments"] = [e for e in data["enrollments"] if e["courseId"] != c["id"]]
            data["grades"] = [g for g in data["grades"] if g["courseId"] != c["id"]]
            _save(data)
            print(f"[ok] Course '{c['title']}' deleted (related enrollments & grades removed).")
        else:
            print("  Cancelled.")


# ---------------------------------------------------------------------------
# STUDENTS
# ---------------------------------------------------------------------------

def cmd_students(args: argparse.Namespace) -> None:
    data = _load()
    students = [u for u in data["users"] if u["role"] == "student"]

    if args.action == "list":
        _header(f"Students ({len(students)} total)")
        for s in students:
            enrolled = sum(1 for e in data["enrollments"] if e["studentId"] == s["id"])
            print(f"  {s['id']:6}  {_col(s['name'], '1'):25}  {s['email']:30}  enrolled={enrolled}")

    elif args.action == "add":
        _header("Add Student")
        s = {
            "id":        _gen_id(),
            "name":      _prompt("Full name"),
            "email":     _prompt("Email"),
            "password":  _prompt("Password", "student123"),
            "role":      "student",
            "createdAt": _now(),
        }
        if not s["name"] or not s["email"]:
            sys.exit("[error] Name and email are required.")
        if any(u["email"] == s["email"] for u in data["users"]):
            sys.exit(f"[error] Email '{s['email']}' already exists.")
        data["users"].append(s)
        _save(data)
        print(f"[ok] Student '{s['name']}' added (id={s['id']}).")

    elif args.action == "delete":
        _header("Delete Student")
        s = _choose(students, "student")
        if s is None:
            return
        confirm = input(f"  Delete '{s['name']}'? (y/N): ").strip().lower()
        if confirm == "y":
            data["users"] = [u for u in data["users"] if u["id"] != s["id"]]
            data["enrollments"] = [e for e in data["enrollments"] if e["studentId"] != s["id"]]
            data["grades"] = [g for g in data["grades"] if g["studentId"] != s["id"]]
            _save(data)
            print(f"[ok] Student '{s['name']}' deleted (related enrollments & grades removed).")
        else:
            print("  Cancelled.")


# ---------------------------------------------------------------------------
# ANNOUNCEMENTS
# ---------------------------------------------------------------------------

def cmd_announcements(args: argparse.Namespace) -> None:
    data = _load()
    announcements = data["announcements"]

    if args.action == "list":
        _header(f"Announcements ({len(announcements)} total)")
        for a in announcements:
            date = a.get("createdAt", "")[:10]
            print(f"  {a['id']:6}  {_col(a['title'], '1'):45}  {date}")

    elif args.action == "add":
        _header("Add Announcement")
        a = {
            "id":        _gen_id(),
            "title":     _prompt("Title"),
            "body":      _prompt("Body"),
            "author":    _prompt("Author", "Admin User"),
            "createdAt": _now(),
        }
        if not a["title"]:
            sys.exit("[error] Title is required.")
        announcements.append(a)
        _save(data)
        print(f"[ok] Announcement '{a['title']}' added.")

    elif args.action == "edit":
        _header("Edit Announcement")
        a = _choose(announcements, "announcement")
        if a is None:
            return
        print("  (Press Enter to keep current value)")
        a["title"]  = _prompt("Title",  a["title"])
        a["body"]   = _prompt("Body",   a["body"])
        a["author"] = _prompt("Author", a["author"])
        _save(data)
        print(f"[ok] Announcement '{a['title']}' updated.")

    elif args.action == "delete":
        _header("Delete Announcement")
        a = _choose(announcements, "announcement")
        if a is None:
            return
        confirm = input(f"  Delete '{a['title']}'? (y/N): ").strip().lower()
        if confirm == "y":
            data["announcements"] = [x for x in announcements if x["id"] != a["id"]]
            _save(data)
            print(f"[ok] Announcement '{a['title']}' deleted.")
        else:
            print("  Cancelled.")


# ---------------------------------------------------------------------------
# ENROLLMENTS
# ---------------------------------------------------------------------------

def cmd_enrollments(args: argparse.Namespace) -> None:
    data = _load()
    enrollments = data["enrollments"]
    students = {u["id"]: u["name"] for u in data["users"] if u["role"] == "student"}
    courses  = {c["id"]: c["title"] for c in data["courses"]}

    if args.action == "list":
        _header(f"Enrollments ({len(enrollments)} total)")
        for e in enrollments:
            sname = students.get(e["studentId"], e["studentId"])
            cname = courses.get(e["courseId"], e["courseId"])
            print(f"  {e['id']:6}  {sname:25}  →  {cname:45}  progress={e.get('progress', 0)}%")

    elif args.action == "add":
        _header("Add Enrollment")
        _header("Select student")
        student_list = [u for u in data["users"] if u["role"] == "student"]
        s = _choose(student_list, "student")
        if s is None:
            return
        _header("Select course")
        c = _choose(data["courses"], "course")
        if c is None:
            return
        if any(e["studentId"] == s["id"] and e["courseId"] == c["id"] for e in enrollments):
            print(f"  [skip] {s['name']} is already enrolled in '{c['title']}'.")
            return
        progress_raw = _prompt("Initial progress % (0–100)", "0")
        try:
            progress = max(0, min(100, int(progress_raw)))
        except ValueError:
            progress = 0
        e = {
            "id":         _gen_id(),
            "studentId":  s["id"],
            "courseId":   c["id"],
            "enrolledAt": _now(),
            "progress":   progress,
        }
        enrollments.append(e)
        _save(data)
        print(f"[ok] {s['name']} enrolled in '{c['title']}' (id={e['id']}).")

    elif args.action == "delete":
        _header("Delete Enrollment")
        display = [
            {**e,
             "_label": f"{students.get(e['studentId'], e['studentId'])} → {courses.get(e['courseId'], e['courseId'])}"}
            for e in enrollments
        ]
        for i, item in enumerate(display):
            print(f"  {i + 1}. {item['_label']}  (id={item['id']})")
        raw = input("  Choose enrollment #: ").strip()
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(enrollments):
                e = enrollments[idx]
                confirm = input(f"  Delete this enrollment? (y/N): ").strip().lower()
                if confirm == "y":
                    data["enrollments"] = [x for x in enrollments if x["id"] != e["id"]]
                    _save(data)
                    print("[ok] Enrollment deleted.")
                else:
                    print("  Cancelled.")
            else:
                print("  Invalid selection.")
        except ValueError:
            print("  Invalid selection.")


# ---------------------------------------------------------------------------
# GRADES
# ---------------------------------------------------------------------------

def cmd_grades(args: argparse.Namespace) -> None:
    data = _load()
    grades    = data["grades"]
    students  = {u["id"]: u["name"] for u in data["users"] if u["role"] == "student"}
    courses   = {c["id"]: c["title"] for c in data["courses"]}

    if args.action == "list":
        _header(f"Grades ({len(grades)} total)")
        for g in grades:
            sname = students.get(g["studentId"], g["studentId"])
            cname = courses.get(g["courseId"], g["courseId"])
            print(f"  {g['id']:6}  {sname:25}  {cname:40}  {g['grade']:5}  score={g.get('score', '—')}")

    elif args.action == "set":
        _header("Set / Update Grade")
        _header("Select student")
        student_list = [u for u in data["users"] if u["role"] == "student"]
        s = _choose(student_list, "student")
        if s is None:
            return
        _header("Select course")
        c = _choose(data["courses"], "course")
        if c is None:
            return
        existing = next((g for g in grades if g["studentId"] == s["id"] and g["courseId"] == c["id"]), None)
        if existing:
            print(f"  Existing grade: {existing['grade']}  score={existing.get('score', '—')}")
            print("  (Press Enter to keep current value)")
            existing["grade"]   = _prompt("Letter grade", existing.get("grade", ""))
            score_raw           = _prompt("Score (0–100)", str(existing.get("score", "")))
            try:
                existing["score"] = int(score_raw)
            except ValueError:
                pass
            existing["gradedAt"] = _now()
            _save(data)
            print(f"[ok] Grade updated: {existing['grade']} / {existing.get('score', '—')}")
        else:
            grade_val = _prompt("Letter grade (A/B+/B/C/D/F)")
            score_raw = _prompt("Score (0–100)", "")
            try:
                score = int(score_raw)
            except ValueError:
                score = None
            entry = {
                "id":        _gen_id(),
                "studentId": s["id"],
                "courseId":  c["id"],
                "grade":     grade_val,
                "gradedAt":  _now(),
            }
            if score is not None:
                entry["score"] = score
            grades.append(entry)
            _save(data)
            print(f"[ok] Grade '{grade_val}' added for {s['name']} in '{c['title']}'.")

    elif args.action == "delete":
        _header("Delete Grade")
        display = [
            {**g,
             "_label": f"{students.get(g['studentId'], g['studentId'])} → {courses.get(g['courseId'], g['courseId'])} [{g['grade']}]"}
            for g in grades
        ]
        for i, item in enumerate(display):
            print(f"  {i + 1}. {item['_label']}  (id={item['id']})")
        raw = input("  Choose grade #: ").strip()
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(grades):
                g = grades[idx]
                confirm = input("  Delete this grade? (y/N): ").strip().lower()
                if confirm == "y":
                    data["grades"] = [x for x in grades if x["id"] != g["id"]]
                    _save(data)
                    print("[ok] Grade deleted.")
                else:
                    print("  Cancelled.")
            else:
                print("  Invalid selection.")
        except ValueError:
            print("  Invalid selection.")


# ---------------------------------------------------------------------------
# EXPORT  (rewrite seed data block in js/app.js)
# ---------------------------------------------------------------------------

_SEED_START = "  /** Initialize with seed data if not already present. */"
_SEED_END   = "  },\n};"   # end of DB object


def cmd_export(_args: argparse.Namespace) -> None:
    data = _load()

    js_path = APP_JS
    if not js_path.exists():
        sys.exit(f"[error] Cannot find {js_path}")

    original = js_path.read_text(encoding="utf-8")
    start_idx = original.find(_SEED_START)
    if start_idx == -1:
        sys.exit("[error] Could not locate the seed-data block in app.js.\n"
                 "Expected comment: /** Initialize with seed data if not already present. */")

    # Build replacement init() body
    def _js_list(items: list) -> str:
        return json.dumps(items, indent=8, ensure_ascii=False)

    seed_block = (
        f"{_SEED_START}\n"
        f"  init() {{\n"
        f"    if (!this.get(this.KEYS.USERS)) {{\n"
        f"      this.set(this.KEYS.USERS, {_js_list(data['users'])});\n"
        f"    }}\n\n"
        f"    if (!this.get(this.KEYS.COURSES)) {{\n"
        f"      this.set(this.KEYS.COURSES, {_js_list(data['courses'])});\n"
        f"    }}\n\n"
        f"    if (!this.get(this.KEYS.ANNOUNCEMENTS)) {{\n"
        f"      this.set(this.KEYS.ANNOUNCEMENTS, {_js_list(data['announcements'])});\n"
        f"    }}\n\n"
        f"    if (!this.get(this.KEYS.ENROLLMENTS)) {{\n"
        f"      this.set(this.KEYS.ENROLLMENTS, {_js_list(data['enrollments'])});\n"
        f"    }}\n\n"
        f"    if (!this.get(this.KEYS.GRADES)) {{\n"
        f"      this.set(this.KEYS.GRADES, {_js_list(data['grades'])});\n"
        f"    }}\n"
        f"  }},\n"
        f"}};"
    )

    # Find end of the init() block (the closing of DB object)
    end_idx = original.find(_SEED_END, start_idx)
    if end_idx == -1:
        sys.exit("[error] Could not find end of DB object in app.js.")

    new_js = original[:start_idx] + seed_block + original[end_idx + len(_SEED_END):]
    js_path.write_text(new_js, encoding="utf-8")
    print(f"[ok] Seed data exported to {js_path}")
    print(f"     Users: {len(data['users'])}  Courses: {len(data['courses'])}  "
          f"Announcements: {len(data['announcements'])}  "
          f"Enrollments: {len(data['enrollments'])}  Grades: {len(data['grades'])}")


# ---------------------------------------------------------------------------
# RESET  (restore default cms_data.json)
# ---------------------------------------------------------------------------

DEFAULT_DATA: dict = {
    "users": [
        {"id": "u1", "name": "Admin User",    "email": "admin@cms.dev",  "password": "admin123",   "role": "admin",   "createdAt": "2025-01-01T00:00:00.000Z"},
        {"id": "u2", "name": "Alice Johnson",  "email": "alice@cms.dev",  "password": "student123", "role": "student", "createdAt": "2025-01-01T00:00:00.000Z"},
        {"id": "u3", "name": "Bob Smith",      "email": "bob@cms.dev",    "password": "student123", "role": "student", "createdAt": "2025-01-01T00:00:00.000Z"},
    ],
    "courses": [
        {"id": "c1", "title": "Introduction to Web Development", "category": "Technology",   "description": "Learn the fundamentals of HTML, CSS, and JavaScript to build modern websites.",           "instructor": "Admin User", "status": "published", "color": "#1f6feb", "createdAt": "2025-01-01T00:00:00.000Z"},
        {"id": "c2", "title": "Data Science Fundamentals",       "category": "Data Science", "description": "A comprehensive introduction to data analysis, visualization, and machine learning basics.", "instructor": "Admin User", "status": "published", "color": "#6e40c9", "createdAt": "2025-01-01T00:00:00.000Z"},
        {"id": "c3", "title": "Business Communication",          "category": "Business",     "description": "Develop professional communication skills for the modern workplace.",                       "instructor": "Admin User", "status": "draft",     "color": "#2da44e", "createdAt": "2025-01-01T00:00:00.000Z"},
    ],
    "announcements": [
        {"id": "a1", "title": "Welcome to the CMS!",  "body": "We are excited to have you here. Explore your courses and get started.",                                     "author": "Admin User", "createdAt": "2025-01-01T00:00:00.000Z"},
        {"id": "a2", "title": "Maintenance Window",   "body": "Scheduled maintenance on Sunday 10pm-12am. The system may be briefly unavailable.", "author": "Admin User", "createdAt": "2025-01-01T00:00:00.000Z"},
    ],
    "enrollments": [
        {"id": "e1", "studentId": "u2", "courseId": "c1", "enrolledAt": "2025-01-01T00:00:00.000Z", "progress": 60},
        {"id": "e2", "studentId": "u2", "courseId": "c2", "enrolledAt": "2025-01-01T00:00:00.000Z", "progress": 25},
        {"id": "e3", "studentId": "u3", "courseId": "c1", "enrolledAt": "2025-01-01T00:00:00.000Z", "progress": 80},
    ],
    "grades": [
        {"id": "g1", "studentId": "u2", "courseId": "c1", "grade": "A",  "score": 92, "gradedAt": "2025-01-01T00:00:00.000Z"},
        {"id": "g2", "studentId": "u3", "courseId": "c1", "grade": "B+", "score": 88, "gradedAt": "2025-01-01T00:00:00.000Z"},
    ],
}


def cmd_reset(_args: argparse.Namespace) -> None:
    confirm = input("Reset ALL content to defaults? This cannot be undone. (y/N): ").strip().lower()
    if confirm == "y":
        _save(DEFAULT_DATA)
        print("[ok] Content reset to defaults.")
    else:
        print("  Cancelled.")


# ---------------------------------------------------------------------------
# SERVE
# ---------------------------------------------------------------------------

def cmd_serve(args: argparse.Namespace) -> None:
    import http.server
    import socketserver
    import threading
    import webbrowser

    port: int = args.port
    directory = str(BASE_DIR)

    class _Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=directory, **kw)

        def log_message(self, fmt, *fmtargs):  # suppress default noisy logs
            print(f"  {self.address_string()}  {fmt % fmtargs}")

    print(f"\n[serve] EduCMS running at http://localhost:{port}")
    print(f"        Admin:   http://localhost:{port}/admin/index.html")
    print(f"        Student: http://localhost:{port}/student/index.html")
    print(f"        Press Ctrl+C to stop.\n")

    def _open():
        import time
        time.sleep(0.5)
        webbrowser.open(f"http://localhost:{port}")

    threading.Thread(target=_open, daemon=True).start()

    with socketserver.TCPServer(("", port), _Handler) as httpd:
        httpd.allow_reuse_address = True
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[serve] Stopped.")


# ---------------------------------------------------------------------------
# CLI WIRING
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="cms_manager.py",
        description="EduCMS content manager — control all website content from the command line.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # serve
    p_serve = sub.add_parser("serve", help="Start a local HTTP server and open the CMS in a browser")
    p_serve.add_argument("--port", type=int, default=8080, help="Port to listen on (default: 8080)")
    p_serve.set_defaults(func=cmd_serve)

    # courses
    p_courses = sub.add_parser("courses", help="Manage courses")
    p_courses.add_argument("action", choices=["list", "add", "edit", "delete"])
    p_courses.set_defaults(func=cmd_courses)

    # students
    p_students = sub.add_parser("students", help="Manage students")
    p_students.add_argument("action", choices=["list", "add", "delete"])
    p_students.set_defaults(func=cmd_students)

    # announcements
    p_ann = sub.add_parser("announcements", help="Manage announcements")
    p_ann.add_argument("action", choices=["list", "add", "edit", "delete"])
    p_ann.set_defaults(func=cmd_announcements)

    # enrollments
    p_enr = sub.add_parser("enrollments", help="Manage student enrollments")
    p_enr.add_argument("action", choices=["list", "add", "delete"])
    p_enr.set_defaults(func=cmd_enrollments)

    # grades
    p_grades = sub.add_parser("grades", help="Manage grades")
    p_grades.add_argument("action", choices=["list", "set", "delete"])
    p_grades.set_defaults(func=cmd_grades)

    # export
    p_export = sub.add_parser("export", help="Write current data/cms_data.json seed into js/app.js")
    p_export.set_defaults(func=cmd_export)

    # reset
    p_reset = sub.add_parser("reset", help="Restore data/cms_data.json to default content")
    p_reset.set_defaults(func=cmd_reset)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

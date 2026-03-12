# EduCMS – Content Management System

A browser-based CMS with a full **Admin Panel** and **Student Portal**, built with HTML, CSS, and vanilla JavaScript. All data is stored in the browser via `localStorage` — no server or build step required.

---

## 🚀 How to Access

### Open the app

Open **`index.html`** in your browser (or serve the repo with any static file server):

```bash
# Python
python3 -m http.server 8080
# then open http://localhost:8080
```

### Login page

The login page (`index.html`) shows a role selector — choose **Admin** or **Student** before signing in.

---

## 🔐 Admin Panel

**URL:** `admin/index.html`

To reach the admin panel, select the **Admin** tab on the login page and sign in with:

| Field    | Value             |
|----------|-------------------|
| Email    | `admin@cms.dev`   |
| Password | `admin123`        |

> 💡 The demo credentials are displayed right on the login page — you can also click **"Quick Login"** to auto-fill them.

### Admin features

| Section          | What you can do                                              |
|------------------|--------------------------------------------------------------|
| **Dashboard**    | Overview stats: total courses, students, enrollments         |
| **Courses**      | Add, edit, and delete courses (title, category, status, color) |
| **Students**     | View all students and their enrollment progress              |
| **Grades**       | Assign or update letter grades and scores per enrollment     |
| **Announcements**| Publish, edit, and delete announcements visible to students  |

---

## 🎓 Student Portal

**URL:** `student/index.html`

Select the **Student** tab on the login page and sign in with:

| Field    | Value               |
|----------|---------------------|
| Email    | `alice@cms.dev`     |
| Password | `student123`        |

### Student features

| Section              | What you can do                                         |
|----------------------|---------------------------------------------------------|
| **Dashboard**        | See enrolled courses, progress, and latest announcements |
| **My Courses**       | View enrolled courses with progress bars; unenroll      |
| **Course Catalog**   | Browse published courses, search, and enroll            |
| **My Grades**        | View grades assigned by the admin                       |
| **Announcements**    | Read announcements posted by the admin                  |

---

## 🐍 Python Content Manager (`cms_manager.py`)

A command-line tool that lets you **control all website content from Python** — no browser required.  
It reads and writes `data/cms_data.json` and can push changes back into `js/app.js` for the next browser session.

### Requirements

Python 3.8+ — only the standard library is used (no `pip install` needed).

### Quick start

```bash
# Start the local server and open the CMS in your browser
python3 cms_manager.py serve

# or on a custom port
python3 cms_manager.py serve --port 3000
```

### Content commands

| Command | Actions | Description |
|---|---|---|
| `python3 cms_manager.py courses` | `list` `add` `edit` `delete` | Manage courses |
| `python3 cms_manager.py students` | `list` `add` `delete` | Manage student accounts |
| `python3 cms_manager.py announcements` | `list` `add` `edit` `delete` | Manage announcements |
| `python3 cms_manager.py enrollments` | `list` `add` `delete` | Manage enrollments |
| `python3 cms_manager.py grades` | `list` `set` `delete` | Assign / update grades |

### Utility commands

```bash
# Push data/cms_data.json → js/app.js (so changes appear on next browser load)
python3 cms_manager.py export

# Restore data/cms_data.json to the default seed content
python3 cms_manager.py reset
```

### Example workflow

```bash
# 1. Add a new course
python3 cms_manager.py courses add

# 2. Add a new student
python3 cms_manager.py students add

# 3. Enroll the student in the course
python3 cms_manager.py enrollments add

# 4. Assign a grade
python3 cms_manager.py grades set

# 5. Export the changes so the browser picks them up
python3 cms_manager.py export

# 6. Open the site
python3 cms_manager.py serve
```

> **Tip:** After running `export`, clear your browser's `localStorage` (DevTools → Application → Storage → Clear site data) so the updated seed is loaded on the next visit.

---

## 📁 Project Structure

```
cms_manager.py      ← Python CLI — controls all CMS content
data/
  cms_data.json     ← Persistent content store (source of truth for the CLI)
index.html          ← Login / role selector
admin/
  index.html        ← Admin panel (SPA)
student/
  index.html        ← Student portal (SPA)
css/
  style.css         ← Shared design system
js/
  app.js            ← Shared data layer (DB, Auth, Utils)
```

---

&copy; 2025 EduCMS &bull; [MIT License](https://gh.io/mit)


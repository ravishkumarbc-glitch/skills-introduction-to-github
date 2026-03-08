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

## 📁 Project Structure

```
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


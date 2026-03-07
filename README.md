# Course CMS

A lightweight Content Management System (CMS) for uploading and managing course content, built with **Python Flask**.

## Features

- **Create & manage courses** — add a title, category, and description for each course
- **Upload course content** — supports PDF, DOCX, MP4, MOV, AVI, PNG, JPG, GIF, TXT, and Markdown files (up to 100 MB each)
- **Drag-and-drop file upload** interface
- **Delete** courses or individual files
- Clean, responsive UI — no JavaScript framework required

## Quick Start

### Prerequisites

- Python 3.9+

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd skills-introduction-to-github

# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
python app.py
```

Open your browser and navigate to **http://127.0.0.1:5000**.

### Configuration

Set the `SECRET_KEY` environment variable before running in any shared environment:

```bash
export SECRET_KEY="your-secret-key-here"
python app.py
```

## Project Structure

```
.
├── app.py              # Flask application
├── requirements.txt    # Python dependencies
├── templates/          # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── course_form.html
│   └── course_detail.html
├── static/
│   ├── css/style.css   # Stylesheet
│   └── js/main.js      # Client-side JavaScript
└── uploads/            # Uploaded files (auto-created, git-ignored)
```

Courses and file metadata are stored in **`courses.json`** (auto-created, git-ignored).

---

&copy; 2025 GitHub &bull; [Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/code_of_conduct.md) &bull; [MIT License](https://gh.io/mit)

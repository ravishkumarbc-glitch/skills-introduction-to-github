/**
 * CMS Application - Shared JavaScript
 * Handles data storage, authentication, and utilities.
 */

/* ==================== DATA STORE ==================== */
const DB = {
  KEYS: {
    USERS: 'cms_users',
    COURSES: 'cms_courses',
    ANNOUNCEMENTS: 'cms_announcements',
    ENROLLMENTS: 'cms_enrollments',
    GRADES: 'cms_grades',
    SESSION: 'cms_session',
  },

  get(key) {
    try {
      return JSON.parse(localStorage.getItem(key) || 'null');
    } catch {
      return null;
    }
  },

  set(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
  },

  /** Initialize with seed data if not already present. */
  init() {
    if (!this.get(this.KEYS.USERS)) {
      this.set(this.KEYS.USERS, [
        { id: 'u1', name: 'Admin User',   email: 'admin@cms.dev',   password: 'admin123',   role: 'admin',   createdAt: new Date().toISOString() },
        { id: 'u2', name: 'Alice Johnson', email: 'alice@cms.dev',   password: 'student123', role: 'student', createdAt: new Date().toISOString() },
        { id: 'u3', name: 'Bob Smith',     email: 'bob@cms.dev',     password: 'student123', role: 'student', createdAt: new Date().toISOString() },
      ]);
    }

    if (!this.get(this.KEYS.COURSES)) {
      this.set(this.KEYS.COURSES, [
        {
          id: 'c1', title: 'Introduction to Web Development', category: 'Technology',
          description: 'Learn the fundamentals of HTML, CSS, and JavaScript to build modern websites.',
          instructor: 'Admin User', status: 'published', color: '#1f6feb',
          createdAt: new Date().toISOString(),
        },
        {
          id: 'c2', title: 'Data Science Fundamentals', category: 'Data Science',
          description: 'A comprehensive introduction to data analysis, visualization, and machine learning basics.',
          instructor: 'Admin User', status: 'published', color: '#6e40c9',
          createdAt: new Date().toISOString(),
        },
        {
          id: 'c3', title: 'Business Communication', category: 'Business',
          description: 'Develop professional communication skills for the modern workplace.',
          instructor: 'Admin User', status: 'draft', color: '#2da44e',
          createdAt: new Date().toISOString(),
        },
      ]);
    }

    if (!this.get(this.KEYS.ANNOUNCEMENTS)) {
      this.set(this.KEYS.ANNOUNCEMENTS, [
        { id: 'a1', title: 'Welcome to the CMS!', body: 'We are excited to have you here. Explore your courses and get started.', createdAt: new Date().toISOString(), author: 'Admin User' },
        { id: 'a2', title: 'Maintenance Window', body: 'Scheduled maintenance on Sunday 10pm–12am. The system may be briefly unavailable.', createdAt: new Date().toISOString(), author: 'Admin User' },
      ]);
    }

    if (!this.get(this.KEYS.ENROLLMENTS)) {
      this.set(this.KEYS.ENROLLMENTS, [
        { id: 'e1', studentId: 'u2', courseId: 'c1', enrolledAt: new Date().toISOString(), progress: 60 },
        { id: 'e2', studentId: 'u2', courseId: 'c2', enrolledAt: new Date().toISOString(), progress: 25 },
        { id: 'e3', studentId: 'u3', courseId: 'c1', enrolledAt: new Date().toISOString(), progress: 80 },
      ]);
    }

    if (!this.get(this.KEYS.GRADES)) {
      this.set(this.KEYS.GRADES, [
        { id: 'g1', studentId: 'u2', courseId: 'c1', grade: 'A', score: 92, gradedAt: new Date().toISOString() },
        { id: 'g2', studentId: 'u3', courseId: 'c1', grade: 'B+', score: 88, gradedAt: new Date().toISOString() },
      ]);
    }
  },
};

/* ==================== AUTH ==================== */
const Auth = {
  login(email, password, role) {
    const users = DB.get(DB.KEYS.USERS) || [];
    const user = users.find(
      u => u.email === email && u.password === password && u.role === role
    );
    if (user) {
      const session = { userId: user.id, name: user.name, email: user.email, role: user.role };
      DB.set(DB.KEYS.SESSION, session);
      return session;
    }
    return null;
  },

  logout() {
    localStorage.removeItem(DB.KEYS.SESSION);
  },

  getSession() {
    return DB.get(DB.KEYS.SESSION);
  },

  requireRole(role) {
    const session = this.getSession();
    if (!session || session.role !== role) {
      window.location.href = '../index.html';
    }
    return session;
  },
};

/* ==================== UTILS ==================== */
const Utils = {
  generateId() {
    if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
      return crypto.randomUUID();
    }
    // Fallback for environments without crypto.randomUUID
    return 'id-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 11);
  },

  formatDate(iso) {
    if (!iso) return '—';
    return new Date(iso).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  },

  escapeHtml(str) {
    const div = document.createElement('div');
    div.appendChild(document.createTextNode(str ?? ''));
    return div.innerHTML;
  },

  showToast(message, type = 'success') {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.className = 'toast-container';
      document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3500);
  },

  openModal(id) {
    const overlay = document.getElementById(id);
    if (overlay) overlay.classList.add('open');
  },

  closeModal(id) {
    const overlay = document.getElementById(id);
    if (overlay) overlay.classList.remove('open');
  },

  setActive(navLinks, page) {
    navLinks.forEach(link => {
      if (link.dataset.page === page) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });
  },

  getInitials(name) {
    if (!name) return '?';
    return name.split(' ').map(w => w[0]).slice(0, 2).join('').toUpperCase();
  },
};

/* ==================== INIT ==================== */
DB.init();

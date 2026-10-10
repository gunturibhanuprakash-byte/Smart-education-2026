# Smart Education — Personalized Learning Platform

An end-to-end modern, responsive web application engineered to transform conventional "one-size-fits-all" education into a **dynamically personalized, adaptive learning journey** for every student, backed by real-time diagnostic analytics for teachers.

---

## 🌟 Key Highlights & Innovations

1. **Adaptive Quiz Engine**:
   - Dynamically scales question difficulty (**Easy &harr; Medium &harr; Hard**) in real-time based on student response accuracy.
   - Provides instant conceptual explanations and live topic mastery recalibration.

2. **Diagnostic Skill Analytics & Visual Radar**:
   - Classifies student proficiency into standard educational bands:
     - `0–39%`: **Very Weak**
     - `40–59%`: **Needs Improvement**
     - `60–74%`: **Average**
     - `75–89%`: **Good**
     - `90–100%`: **Excellent**
   - Interactive radar, bar, and line charts powered by Chart.js.

3. **Personalized Learning & Recommendation Engine**:
   - Analyzes weak topics and automatically recommends targeted video lessons, notes, step-by-step examples, and practice drills.

4. **Dual-Mode AI Tutor & Question Generator**:
   - **Level-Adaptive AI Tutor**: Delivers simple everyday analogies for beginners and rigorous technical breakdowns for advanced learners.
   - **Zero-Dependency Fallback**: Built-in comprehensive knowledge engine covering C Programming, Data Structures, Mathematics, and Physics that works 100% out of the box even without external API keys.
   - **AI Question Generation**: Allows teachers to draft new questions with explanations in seconds.

5. **Multilingual Localization**:
   - Real-time language switching supporting **English**, **Telugu (తెలుగు)**, and **Hindi (हिन्दी)**.

6. **Low-Connectivity & Offline PWA Ready**:
   - Service worker caching, local storage offline quiz data, and responsive connection status indicator (**ONLINE** / **OFFLINE MODE**).

---

## 🛠️ Technology Stack

- **Backend**: Python 3.12, Flask, Werkzeug, python-dotenv, requests
- **Database**: SQLite 3 (Normalized relational schema with foreign key constraints and indexes)
- **Frontend**: HTML5, CSS3 (Modern Glassmorphism & Custom CSS variables design system), Vanilla JavaScript (ES6+)
- **Visualizations**: Chart.js & FontAwesome 6 Icons

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Ensure Python 3.9+ is installed on your machine.

### 2. Clone & Install Dependencies
```bash
# Navigate to the project folder
cd "path/to/smart-education"

# Install dependencies
pip install -r requirements.txt
```

### 3. Initialize & Seed Sample Data
Populate the database with realistic students, subjects, questions, marks, and materials:
```bash
python database/seed.py
```

### 4. Run the Web Application
```bash
python app.py
```
Open your browser and navigate to: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🔑 Pre-Configured Demo Accounts

For instant hackathon demonstration, click the 1-click demo filler buttons on the login page or use the credentials below:

| Role | Username | Password | Profile Highlights |
| :--- | :--- | :--- | :--- |
| **Student** | `student1` | `student123` | Rahul Sharma (CSE, Sem 4) &bull; Strong in Arrays, Weak in Pointers & Recursion |
| **Student** | `student2` | `student123` | Priya Patel (CSE, Sem 4) &bull; Top Performer (92.5%) |
| **Student** | `student5` | `student123` | Vikram Singh (CSE, Sem 4) &bull; At-risk student requiring teacher support |
| **Teacher** | `teacher1` | `teacher123` | Prof. Arvind Swaminathan &bull; Computer Science & Engineering |

---

## 📁 Project Architecture

```
smart-education/
│
├── app.py                      # Flask Application Entrypoint & Blueprints
├── requirements.txt            # Python Dependencies
├── .env.example                # Sample environment configuration
├── README.md                   # Full Documentation & Presentation Guide
│
├── database/
│   ├── db.py                   # SQLite Connection & Helper context managers
│   ├── schema.sql              # Clean relational database schema
│   └── seed.py                 # Comprehensive seed data script
│
├── services/
│   ├── performance_service.py  # Student analytics & topic mastery bands
│   ├── recommendation_service.py # Personalized study recommendation engine
│   ├── adaptive_quiz_service.py# Dynamic difficulty scaling algorithm
│   └── ai_service.py           # Level-adaptive AI Tutor & Question Generator
│
├── routes/
│   ├── auth_routes.py          # Authentication, sessions, & role decorators
│   ├── student_routes.py       # Student dashboard, subjects, marks, performance
│   ├── quiz_routes.py          # Adaptive quiz flows & live feedback submission
│   ├── teacher_routes.py       # Teacher dashboard, student inspection, CRUD
│   └── api_routes.py           # AI chat, Question gen, & offline data endpoints
│
├── templates/
│   ├── base.html               # Master layout (sidebar, status pill, lang switcher)
│   ├── login.html              # Modern login portal with 1-click demo credentials
│   ├── student/
│   │   ├── dashboard.html      # KPIs, radar mastery chart, subjects, alerts
│   │   ├── subjects.html       # Enrolled subjects grid
│   │   ├── subject_detail.html # Single subject deep-dive, topics, materials
│   │   ├── marks.html          # Full gradebook & cumulative score table
│   │   ├── performance.html    # In-depth topic classification & spectrum
│   │   ├── learning.html       # Filterable learning resources & video hub
│   │   ├── quiz_start.html     # Adaptive quiz configuration launcher
│   │   ├── quiz_active.html    # Live quiz screen with instant explanation box
│   │   ├── quiz_result.html    # Post-quiz scorecard & difficulty path timeline
│   │   └── ai_tutor.html       # AI Chatbot with level toggle & prompt presets
│   └── teacher/
│       ├── dashboard.html      # Class analytics, class average, at-risk alerts
│       ├── students.html       # Students directory & performance badges
│       ├── student_detail.html # Individual student diagnostic file
│       ├── questions.html      # Question Bank CRUD & AI Question Generator
│       ├── materials.html      # Learning Materials CRUD & video links
│       └── marks_manage.html   # Marks management & GPA recalculation
│
├── static/
│   ├── css/
│   │   ├── style.css           # Global design system & responsive layout
│   │   └── components.css      # Quiz tiles, AI chat bubbles, badges, modals
│   ├── js/
│   │   ├── app.js              # Sidebar toggle, modal handlers, demo fillers
│   │   ├── charts.js           # Chart.js radar, bar, and line chart helpers
│   │   ├── adaptive_quiz.js    # Client-side quiz evaluation & timer
│   │   ├── ai_tutor.js         # Interactive AI chat handling & prompt chips
│   │   ├── translations.js     # Multilingual dictionary (EN, TE, HI)
│   │   └── offline.js          # Online/offline status listener & caching
│   └── sw.js                   # Service Worker for offline asset caching
│
└── tests/
    └── test_app.py             # Automated unit tests for all core services
```

---

## 🧪 Running Automated Tests

Run the comprehensive unit test suite:
```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## 🏆 Hackathon Presentation Flow

1. **Student Experience**:
   - Log in using **Student (Rahul)** demo button.
   - Show the **Dashboard**: Highlight the **Topic Mastery Radar Chart**, **Streak Tracker**, and **Identified Weak Topics** (e.g. *Pointers* & *Recursion*).
   - Launch an **Adaptive Quiz** on *C Programming*:
     - Demonstrate starting on **Easy**.
     - Answer correctly &rarr; difficulty dynamically shifts to **Medium** and **Hard**.
     - Show **Instant Explanation** drawer appearing after submission.
     - View the **Quiz Result Scorecard** with the difficulty progression path and auto-suggested next lesson.
   - Open **AI Tutor**: Select *Beginner* level & click "Pointers Analogy" &rarr; see instant visual explanation.
   - Switch language to **తెలుగు (Telugu)** or **हिन्दी (Hindi)** &rarr; see live UI localization.

2. **Teacher Experience**:
   - Log in as **Teacher (Prof. Arvind)**.
   - Show the **Teacher Dashboard**: Class average, lowest scoring topics, and **At-Risk Students** list.
   - Open **Student Diagnostic File** for `student5` &rarr; review weak topics for teacher intervention.
   - Open **Question Bank** &rarr; open **AI Question Generator** &rarr; select Subject/Topic/Difficulty & generate draft questions with explanations.
